from dataclasses import dataclass
from typing import Literal

from type.metrics import TTFT, Latency, Token


@dataclass
class Report:
    model: str
    completion_type: Literal["chat", "generate"]
    max_tokens: int
    num_concurrency: int
    total_requests: int
    total_duration_time: int
    dataset: str
    successful_requests: int
    request_per_sec: float
    throughput_token: float
    ttft: TTFT
    latency: Latency
    token: Token
