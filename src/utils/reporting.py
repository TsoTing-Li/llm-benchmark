import json
import time
from pathlib import Path
from typing import Literal

from anyio import open_file

from type.metrics import TTFT, Latency, Stats, Token
from type.report import Report
from utils.lmcache import get_lmcache_metrics
from utils.utils import extract_ip_from_url


def generate_test_report(
    model_server: str,
    current_time: str,
    run_label: Literal["cold", "warm", "single"],
    model: str,
    completion_type: Literal["chat", "generate"],
    max_tokens: int,
    num_concurrency: int,
    stats: Stats,
    duration: float,
    dataset: str,
    prompt: str,
    ttft_list: list[float],
    latency_list: list[float],
    token_list: list[int],
    stop_reason: Literal["done", "cancelled", "error"],
    use_lmcache: bool = False,
) -> Report:
    rps = stats.finished_requests / duration if duration > 0 else 0.0

    if ttft_list:
        avg_ttft = round(sum(ttft_list) / len(ttft_list) * 1000, 2)
        max_ttft = round(max(ttft_list) * 1000, 2)
        min_ttft = round(min(ttft_list) * 1000, 2)
    else:
        avg_ttft = None
        max_ttft = None
        min_ttft = None
    ttft = TTFT(
        avg_ttft=avg_ttft,
        max_ttft=max_ttft,
        min_ttft=min_ttft,
    )

    if latency_list:
        avg_latency = round(sum(latency_list) / len(latency_list), 2)
        max_latency = round(max(latency_list), 2)
        min_latency = round(min(latency_list), 2)
    else:
        avg_latency = None
        max_latency = None
        min_latency = None
    latency = Latency(
        avg_latency=avg_latency,
        max_latency=max_latency,
        min_latency=min_latency,
    )

    if token_list:
        avg_token = round(sum(token_list) / len(token_list), 2)
        max_token = max(token_list)
        min_token = min(token_list)
    else:
        avg_token = None
        max_token = None
        min_token = None
    token = Token(
        avg_token=avg_token,
        max_token=max_token,
        min_token=min_token,
    )

    throughput_token = (
        round(sum(token_list) / sum(latency_list), 2) if sum(latency_list) > 0 else 0.0
    )

    if use_lmcache:
        lmcache_host = extract_ip_from_url(url=model_server)
        lmcache_metrics = None
        if lmcache_host is not None:
            time.sleep(10)
            lmcache_metrics = get_lmcache_metrics(lmcache_host=lmcache_host)
    else:
        lmcache_metrics = None

    return Report(
        model_server=model_server,
        current_time=current_time,
        stop_reason=stop_reason,
        run_label=run_label,
        model=model,
        completion_type=completion_type,
        max_tokens=max_tokens,
        num_concurrency=num_concurrency,
        total_duration_time=round(duration, 2),
        dataset=dataset if dataset else prompt,
        request_per_sec=round(rps, 2),
        throughput_token=throughput_token,
        stats=stats,
        ttft=ttft,
        latency=latency,
        token=token,
        lmcache_metrics=lmcache_metrics,
    )


async def save_report_as_file(data: Report, save_path: str) -> None:
    report_content = {
        "Model server": data.model_server,
        "Date": data.current_time,
        "Stop reason": data.stop_reason,
        "Run label": data.run_label,
        "Model": data.model,
        "Completion type": data.completion_type,
        "Limit output tokens": data.max_tokens,
        "Number of concurrency": data.num_concurrency,
        "Duration time (s)": data.total_duration_time,
        "Dataset": data.dataset,
        "Request per second (req/s)": data.request_per_sec,
        "Throughput token (tok/s)": data.throughput_token,
        "Stats": {
            "Started requests": data.stats.started_requests,
            "Finished requests": data.stats.finished_requests,
            "Successful requests": data.stats.successful_requests,
            "Failed requests": data.stats.failed_requests,
            "Timeout requests": data.stats.timeout_requests,
            "Non-200 requests": data.stats.non_200_requests,
            "Cancelled requests": data.stats.cancelled_requests,
        },
        "TTFT": {
            "Avg ttft (ms)": data.ttft.avg_ttft,
            "Max ttft (ms)": data.ttft.max_ttft,
            "Min ttft (ms)": data.ttft.min_ttft,
        },
        "Latency": {
            "Avg latency (s)": data.latency.avg_latency,
            "Max latency (s)": data.latency.max_latency,
            "Min latency (s)": data.latency.min_latency,
        },
        "Token": {
            "Avg token (tok/req)": data.token.avg_token,
            "Max token (tok/req)": data.token.max_token,
            "Min token (tok/req)": data.token.min_token,
        },
    }

    if data.lmcache_metrics is not None:
        lmcache_report = {
            "LMCache Metrics": {
                "Num lookup hits total": data.lmcache_metrics.raw_data.num_lookup_hits_total,
                "Num lookup tokens total": data.lmcache_metrics.raw_data.num_lookup_tokens_total,
                "Num hit tokens total": data.lmcache_metrics.raw_data.num_hit_tokens_total,
                "Num retrieve requests total": data.lmcache_metrics.raw_data.num_retrieve_requests_total,
                "Num store requests total": data.lmcache_metrics.raw_data.num_store_requests_total,
                "Local CPU evict count total": data.lmcache_metrics.raw_data.local_cpu_evict_count_total,
                "Prefix hit ratio": data.lmcache_metrics.prefix_hit_ratio,
                "Retrieve hit ratio": data.lmcache_metrics.retrieve_hit_ratio,
                "Retrieve tokens per hit": data.lmcache_metrics.retrieve_tokens_per_hit,
                "Evict ratio": data.lmcache_metrics.evict_ratio,
            },
        }
        report_content.update(lmcache_report)

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    async with await open_file(save_path, "w") as f:
        encode_data = json.dumps(report_content, indent=2, ensure_ascii=True)
        await f.write(encode_data)


def show_report(report: Report) -> None:
    report_content = f"""
***** 📊 REPORT *****
Model server: {report.model_server}
Date: {report.current_time}
Stop reason: {report.stop_reason}
Run label: {report.run_label}
Model: {report.model}
Limit output tokens: {report.max_tokens}
Num concurrency: {report.num_concurrency}
Duration time (s): {report.total_duration_time}
Dataset: {report.dataset}
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

    if report.lmcache_metrics is not None:
        lmcache_report = f"""
***** LMCache METRICS *****
Prefix hit ratio: {report.lmcache_metrics.prefix_hit_ratio}
Retrieve hit ratio: {report.lmcache_metrics.retrieve_hit_ratio}
Retrieve tokens per hit: {report.lmcache_metrics.retrieve_tokens_per_hit}
Evict ratio: {report.lmcache_metrics.evict_ratio}
    """
        report_content += lmcache_report

    print(report_content)
