import argparse
import asyncio
import os
import time

import httpx

from type.run_args import Args
from utils.client_openai import build_payload, request_openai_format
from utils.datasets import build_dataset
from utils.errors import save_error_as_file
from utils.progress import text_progress_bar
from utils.reporting import generate_test_report, save_report_as_file


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
    ttft_list: list[float] = list()
    latencies: list[float] = list()
    tokens: list[int] = list()
    error_record: list[dict] = list()

    async def worker(
        aclient: httpx.AsyncClient,
        url: str,
        headers: dict,
        timeout: int,
        error_record: list[dict],
    ):
        prompt = next(test_datasets_cycle)
        payload = build_payload(
            completion_type=completion_type, prompt=prompt, args=args
        )
        async with semaphore:
            _ttft, _latency, _token = await request_openai_format(
                aclient=aclient,
                url=url,
                headers=headers,
                payload=payload,
                timeout=timeout,
                error_record=error_record,
            )

            if _latency is not None and _token is not None:
                ttft_list.append(_ttft)
                latencies.append(_latency)
                tokens.append(_token)

    progress = 0
    lock = asyncio.Lock()

    async def worker_with_progress():
        nonlocal progress
        await worker(
            aclient=aclient,
            url=url,
            headers=headers,
            timeout=args.timeout,
            error_record=error_record,
        )
        async with lock:
            progress += 1
            print(
                f"\r{text_progress_bar(progress=progress, total=args.num_request)} {progress}/{args.num_request}",
                end="",
                flush=True,
            )

    async with httpx.AsyncClient() as aclient:
        print("\n✅ Check model-server")
        warmup_payload = build_payload(
            completion_type=completion_type, prompt=args.prompt, args=args
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
            print("Check model-server failed")
            return

        print("\n===== 🏃 Start benchmark process =====")
        stress_test_start_time = time.perf_counter()

        try:
            if args.num_request >= 1:
                tasks = [
                    asyncio.create_task(worker_with_progress())
                    for _ in range(args.num_request)
                ]
                await asyncio.gather(*tasks)
                print()
            elif args.duration_time >= 1:

                async def print_timer(duration: int):
                    for i in range(duration):
                        print(
                            f"\rElapsed time: {i + 1}/{duration} sec",
                            end="",
                            flush=True,
                        )
                        asyncio.sleep(1)
                    print()

                stress_test_end_time = stress_test_start_time + args.duration_time

                async def loop_stress_test():
                    while time.perf_counter() < stress_test_end_time:
                        await worker(
                            aclient=aclient,
                            url=url,
                            headers=headers,
                            timeout=args.timeout,
                            error_record=error_record,
                        )

                timer_task = asyncio.create_task(
                    print_timer(duration=args.duration_time)
                )
                loop_stress_test_runners = [
                    asyncio.create_task(loop_stress_test())
                    for _ in range(args.concurrency)
                ]
                await asyncio.gather(*loop_stress_test_runners, timer_task)

        except KeyboardInterrupt:
            print("\n❗ Detected KeyboardInterrupt, generating report...")

        finally:
            stress_test_end = time.perf_counter()

            report = generate_test_report(
                model=args.model,
                max_tokens=args.max_tokens,
                num_concurrency=args.concurrency,
                requests=args.num_request,
                duration=stress_test_end - stress_test_start_time,
                dataset=os.path.basename(args.dataset_path),
                prompt=args.prompt,
                ttft_list=ttft_list,
                latency_list=latencies,
                token_list=tokens,
            )

            report_content = f"""
***** 📊 REPORT *****
Model: {report.model}
Limit output tokens: {report.max_tokens}
Num concurrency: {report.num_concurrency}
Total requests: {report.total_requests}
Duration time (s): {report.total_duration_time}
Dataset: {report.dataset if report.dataset else args.prompt}
Successful requests: {report.successful_requests}
Request per second (req/s): {report.request_per_sec}
Throughput token (tok/s): {report.throughput_token}
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

            if error_record:
                await save_error_as_file(error_data=error_record)
                print(
                    "\n❗ Some errors received during the benchmark test, recorded in error.jsonl"
                )

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
    parse.add_argument("--timeout", type=int, default=30)
    parse.add_argument("--prompt", type=str, default="how are you?")
    parse.add_argument("--dataset_path", type=str, default="")
    parse.add_argument("--num_request", type=int, default=100)
    parse.add_argument("--duration_time", type=int, default=0)
    parse.add_argument("--max_tokens", type=int, default=32)
    parse.add_argument("--temperature", type=float, default=0.7)
    parse.add_argument("--output_file", type=str, default="./report.json")

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
        print(f"\n❌ Unexpected error: {e}")
