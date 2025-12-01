from dataclasses import dataclass
from typing import Literal

from type.metrics import TTFT, Latency, LMCache, Stats, Token


@dataclass
class Report:
    model_server: str
    current_time: str
    stop_reason: Literal["done", "cancelled", "error"]
    run_label: Literal["cold", "warm", "single"]
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
    lmcache_metrics: LMCache | None = None
