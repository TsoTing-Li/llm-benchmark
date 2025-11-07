import json
from typing import Literal

from anyio import open_file

from type.metrics import TTFT, Latency, Token
from type.report import Report


def generate_test_report(
    model: str,
    completion_type: Literal["chat", "generate"],
    max_tokens: int,
    num_concurrency: int,
    requests: int,
    duration: float,
    dataset: str,
    prompt: str,
    ttft_list: list[float],
    latency_list: list[float],
    token_list: list[int],
) -> Report:
    ttft = TTFT(
        avg_ttft=round(sum(ttft_list) / len(ttft_list) * 1000, 2),
        max_ttft=round(max(ttft_list) * 1000, 2),
        min_ttft=round(min(ttft_list) * 1000, 2),
    )

    latency = Latency(
        avg_latency=round(sum(latency_list) / len(latency_list), 2),
        max_latency=round(max(latency_list), 2),
        min_latency=round(min(latency_list), 2),
    )

    token = Token(
        avg_token=round(sum(token_list) / len(token_list), 2),
        max_token=max(token_list),
        min_token=min(token_list),
    )

    return Report(
        model=model,
        completion_type=completion_type,
        max_tokens=max_tokens,
        num_concurrency=num_concurrency,
        total_requests=requests,
        total_duration_time=round(duration, 2),
        dataset=dataset if dataset else prompt,
        successful_requests=len(latency_list),
        request_per_sec=round(requests / duration, 2),
        throughput_token=round(sum(token_list) / sum(latency_list), 2),
        ttft=ttft,
        latency=latency,
        token=token,
    )


async def save_report_as_file(data: Report, save_path: str) -> None:
    report_content = {
        "Model": data.model,
        "Completion type": data.completion_type,
        "Limit output tokens": data.max_tokens,
        "Number of concurrency": data.num_concurrency,
        "Total requests": data.total_requests,
        "Duration time (s)": data.total_duration_time,
        "Dataset": data.dataset,
        "Successful requests": data.successful_requests,
        "Request per second (req/s)": data.request_per_sec,
        "Throughput token (tok/s)": data.throughput_token,
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
    async with await open_file(save_path, "w") as f:
        encode_data = json.dumps(report_content, indent=2, ensure_ascii=True)
        await f.write(encode_data)
