import argparse
import asyncio
import os
import time
import traceback
from datetime import datetime
from typing import Literal

import httpx
import tqdm

from type.metrics import Stats
from type.run_args import Args
from utils.client_openai import build_payload, request_openai_format
from utils.datasets import build_dataset
from utils.reporting import generate_test_report, save_report_as_file
from utils.utils import verbose_log


async def main(args: Args) -> None:
    assert args.concurrency >= 1, (
        f"concurrency is {args.concurrency}, must be greater than or equal to 1."
    )
    assert args.num_request >= 1 or args.duration_time >= 1, (
        "num_request or duration_time must be greater than or equal to 1."
    )
    assert args.max_tokens >= 1, (
        f"max_tokens is {args.max_tokens}, must be greater than or equal to 1."
    )
    assert args.temperature >= 0.0, (
        f"temperature is {args.temperature}, must be greater than or equal 0.0."
    )

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n🛠️  Building datasets")
    test_datasets_cycle = await build_dataset(
        path=args.dataset_path, prompt=args.prompt
    )

    url = args.base_url.strip("/") + args.endpoint
    headers = {"Content-Type": "application/json"}
    if args.api_key is not None:
        headers.update({"Authorization": f"Bearer {args.api_key}"})
    completion_type = "chat" if args.endpoint == "/v1/chat/completions" else "generate"

    semaphore = asyncio.Semaphore(args.concurrency)

    stats = Stats()
    requests_lock = asyncio.Lock()

    ttft_list: list[float] = list()
    latencies: list[float] = list()
    tokens: list[int] = list()

    async def worker(
        semaphore: asyncio.Semaphore,
        aclient: httpx.AsyncClient,
        url: str,
        headers: dict,
        timeout: int,
        pbar: tqdm.tqdm | None = None,
        mode: Literal["duration_time", "num_request"] = "num_request",
    ):
        prompt = next(test_datasets_cycle)
        payload = build_payload(
            completion_type=completion_type, prompt=prompt, args=args
        )
        async with semaphore:
            async with requests_lock:
                stats.started_requests += 1

            try:
                _ttft, _latency, _token = await request_openai_format(
                    aclient=aclient,
                    url=url,
                    headers=headers,
                    payload=payload,
                    timeout=timeout,
                )
            except asyncio.CancelledError:
                err_msg = "Request cancelled by user"
                async with requests_lock:
                    stats.cancelled_requests += 1

                verbose_log(msg=err_msg, pbar=pbar, verbose=args.verbose)
                raise
            except httpx.ConnectTimeout:
                err_msg = "Request failed: ConnectTimeout (DNS/TCP/TLS handshake)"
                async with requests_lock:
                    stats.timeout_requests += 1
                    stats.failed_requests += 1
                    stats.finished_requests += 1

                    if pbar is not None:
                        pbar.set_postfix(
                            started=stats.started_requests,
                            successful=stats.successful_requests,
                            failed=stats.failed_requests,
                            timeout=stats.timeout_requests,
                            non_200=stats.non_200_requests,
                        )
                        if mode == "num_request":
                            pbar.update(1)

                verbose_log(msg=err_msg, pbar=pbar, verbose=args.verbose)
                return
            except httpx.WriteTimeout:
                err_msg = "Request failed: WriteTimeout (likely while sending the request body)"
                async with requests_lock:
                    stats.timeout_requests += 1
                    stats.failed_requests += 1
                    stats.finished_requests += 1

                    if pbar is not None:
                        pbar.set_postfix(
                            started=stats.started_requests,
                            successful=stats.successful_requests,
                            failed=stats.failed_requests,
                            timeout=stats.timeout_requests,
                            non_200=stats.non_200_requests,
                        )
                        if mode == "num_request":
                            pbar.update(1)

                verbose_log(msg=err_msg, pbar=pbar, verbose=args.verbose)
                return
            except httpx.PoolTimeout:
                err_msg = (
                    "Request failed: PoolTimeout (no available connection in pool)"
                )
                async with requests_lock:
                    stats.timeout_requests += 1
                    stats.failed_requests += 1
                    stats.finished_requests += 1

                    if pbar is not None:
                        pbar.set_postfix(
                            started=stats.started_requests,
                            successful=stats.successful_requests,
                            failed=stats.failed_requests,
                            timeout=stats.timeout_requests,
                            non_200=stats.non_200_requests,
                        )
                        if mode == "num_request":
                            pbar.update(1)

                verbose_log(msg=err_msg, pbar=pbar, verbose=args.verbose)
                return
            except asyncio.TimeoutError:
                err_msg = (
                    "Request failed: TimeoutError (overall request timeout exceeded)"
                )
                async with requests_lock:
                    stats.timeout_requests += 1
                    stats.failed_requests += 1
                    stats.finished_requests += 1

                    if pbar is not None:
                        pbar.set_postfix(
                            started=stats.started_requests,
                            successful=stats.successful_requests,
                            failed=stats.failed_requests,
                            timeout=stats.timeout_requests,
                            non_200=stats.non_200_requests,
                        )
                        if mode == "num_request":
                            pbar.update(1)

                verbose_log(msg=err_msg, pbar=pbar, verbose=args.verbose)
                return
            except httpx.HTTPStatusError as e:
                err_msg = f"Request failed: HTTPStatusError (status code: {e.response.status_code}, mes: {e})"
                async with requests_lock:
                    stats.failed_requests += 1
                    stats.non_200_requests += 1
                    stats.finished_requests += 1

                    if pbar is not None:
                        pbar.set_postfix(
                            started=stats.started_requests,
                            successful=stats.successful_requests,
                            failed=stats.failed_requests,
                            timeout=stats.timeout_requests,
                            non_200=stats.non_200_requests,
                        )
                        if mode == "num_request":
                            pbar.update(1)

                verbose_log(msg=err_msg, pbar=pbar, verbose=args.verbose)
                return
            except Exception as e:
                err_msg = str(e)
                async with requests_lock:
                    stats.failed_requests += 1
                    stats.finished_requests += 1

                    if pbar is not None:
                        pbar.set_postfix(
                            started=stats.started_requests,
                            successful=stats.successful_requests,
                            failed=stats.failed_requests,
                            timeout=stats.timeout_requests,
                        )
                        if mode == "num_request":
                            pbar.update(1)

                verbose_log(msg=err_msg, pbar=pbar, verbose=args.verbose)
                return

        ttft_list.append(_ttft)
        latencies.append(_latency)
        tokens.append(_token)

        async with requests_lock:
            stats.successful_requests += 1
            stats.finished_requests += 1

            if pbar is not None:
                pbar.set_postfix(
                    started=stats.started_requests,
                    successful=stats.successful_requests,
                    failed=stats.failed_requests,
                    timeout=stats.timeout_requests,
                    non_200=stats.non_200_requests,
                )
                if mode == "num_request":
                    pbar.update(1)

    async with httpx.AsyncClient() as aclient:
        try:
            print("\n✅ Check model-server")
            warmup_payload = build_payload(
                completion_type=completion_type, prompt="how are you?", args=args
            )
            (
                test_ttft,
                test_latency,
                test_token,
            ) = await request_openai_format(
                aclient=aclient,
                url=url,
                headers=headers,
                payload=warmup_payload,
                timeout=args.timeout,
            )
            if test_ttft is None or test_latency is None or test_token is None:
                raise RuntimeError("Check model-server failed")
        except httpx.HTTPStatusError as e:
            print(f"\n❌ Non-200 status code received: {e.response.status_code}")
            return
        except Exception as e:
            print(f"\n❌ {e}")
            return

        print("\n===== 🏃 Start benchmark process =====")
        stress_test_start_time = time.perf_counter()

        try:
            if args.duration_time >= 1:

                async def loop_stress_test(end_time: float, pbar: tqdm.tqdm):
                    while time.perf_counter() < end_time:
                        await worker(
                            semaphore=semaphore,
                            aclient=aclient,
                            url=url,
                            headers=headers,
                            timeout=args.timeout,
                            pbar=pbar,
                            mode="duration_time",
                        )

                stress_test_end_time = stress_test_start_time + args.duration_time

                async def timer_progress(duration: int, pbar: tqdm.tqdm) -> None:
                    for sec in range(duration):
                        await asyncio.sleep(1)
                        pbar.update(1)

                    pbar.n = duration
                    pbar.refresh()

                with tqdm.tqdm(
                    total=args.duration_time,
                    desc="Benchmark runner",
                    unit="sec",
                    leave=True,
                ) as pbar:
                    loop_stress_test_runners = [
                        asyncio.create_task(
                            loop_stress_test(end_time=stress_test_end_time, pbar=pbar)
                        )
                        for _ in range(args.concurrency)
                    ]
                    timer_task = asyncio.create_task(
                        timer_progress(duration=args.duration_time, pbar=pbar)
                    )
                    await asyncio.gather(*loop_stress_test_runners, timer_task)
            elif args.num_request >= 1:
                with tqdm.tqdm(
                    total=args.num_request,
                    desc="Benchmark runner",
                    leave=True,
                ) as pbar:
                    tasks = [
                        asyncio.create_task(
                            worker(
                                semaphore=semaphore,
                                aclient=aclient,
                                url=url,
                                headers=headers,
                                timeout=args.timeout,
                                pbar=pbar,
                                mode="num_request",
                            )
                        )
                        for _ in range(args.num_request)
                    ]
                    await asyncio.gather(*tasks)

        except asyncio.CancelledError:
            print("\n❗ Detected KeyboardInterrupt, generating report...")

        finally:
            stress_test_end = time.perf_counter()

            report = generate_test_report(
                current_time=current_time,
                model=args.model,
                completion_type=completion_type,
                max_tokens=args.max_tokens,
                num_concurrency=args.concurrency,
                stats=stats,
                duration=stress_test_end - stress_test_start_time,
                dataset=os.path.basename(args.dataset_path),
                prompt=args.prompt,
                ttft_list=ttft_list,
                latency_list=latencies,
                token_list=tokens,
            )

            report_content = f"""
***** 📊 REPORT *****
Date: {report.current_time}
Model: {report.model}
Limit output tokens: {report.max_tokens}
Num concurrency: {report.num_concurrency}
Duration time (s): {report.total_duration_time}
Dataset: {report.dataset if report.dataset else args.prompt}
Request per second (req/s): {report.request_per_sec}
Throughput token (tok/s): {report.throughput_token}
***** STATS *****
Started requests: {report.stats.started_requests}
Finished requests: {report.stats.finished_requests}
Successful requests: {report.stats.successful_requests}
Failed requests: {report.stats.failed_requests}
Timeout requests: {report.stats.timeout_requests}
Non-200 requests: {report.stats.non_200_requests}
Cancelled requests: {report.stats.cancelled_requests}
***** TIME TO FIRST TOKEN *****
Avg ttft (ms): {report.ttft.avg_ttft}
Max ttft (ms): {report.ttft.max_ttft}
Min ttft (ms): {report.ttft.min_ttft}
***** LATENCY *****
Avg latency (ms): {report.latency.avg_latency}
Max latency (ms): {report.latency.max_latency}
Min latency (ms): {report.latency.min_latency}
***** TOKEN *****
Avg token (tok/req): {report.token.avg_token}
Max token (tok/req): {report.token.max_token}
Min token (tok/req): {report.token.min_token}
                    """
            print("\n", report_content.strip())

            if args.output_file:
                await save_report_as_file(data=report, save_path=args.output_file)
                print(f"\n📄 Save report file in {args.output_file}")


def build_parse() -> Args:
    parse = argparse.ArgumentParser()

    parse.add_argument("--base_url", required=True, type=str)
    parse.add_argument(
        "--endpoint",
        type=str,
        choices=["/v1/chat/completions", "/v1/completions"],
        default="/v1/chat/completions",
    )
    parse.add_argument("--api_key", type=str, default=None)
    parse.add_argument("--model", required=True, type=str)
    parse.add_argument("--concurrency", type=int, default=16)
    parse.add_argument("--timeout", type=int, default=120)
    parse.add_argument("--prompt", type=str, default="how are you?")
    parse.add_argument("--dataset_path", type=str, default="")
    parse.add_argument("--num_request", type=int, default=100)
    parse.add_argument("--duration_time", type=int, default=0)
    parse.add_argument("--max_tokens", type=int, default=32)
    parse.add_argument("--temperature", type=float, default=0.7)
    parse.add_argument("--output_file", type=str, default="./report.json")
    parse.add_argument(("--verbose"), action="store_true", default=False)

    args = parse.parse_args()
    print(args)

    return Args(**vars(args))


if __name__ == "__main__":
    args = build_parse()
    try:
        asyncio.run(main(args=args))
    except KeyboardInterrupt:
        print("\n❗ User interrupted")
    except Exception as e:
        traceback.print_exc()
        print(f"\n❌ Unexpected error: {e}")
