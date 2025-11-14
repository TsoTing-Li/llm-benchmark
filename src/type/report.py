from dataclasses import dataclass
from typing import Literal

from type.metrics import TTFT, Latency, Stats, Token


@dataclass
class Report:
    current_time: str
    model: str
    completion_type: Literal["chat", "generate"]
    max_tokens: int
    num_concurrency: int
    total_duration_time: int
    dataset: str
    request_per_sec: float
    throughput_token: float
    stats: Stats
    ttft: TTFT
    latency: Latency
    token: Token
