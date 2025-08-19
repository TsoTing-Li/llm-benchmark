from dataclasses import dataclass


@dataclass
class TTFT:
    # Time to first token (ms)
    avg_ttft: float
    max_ttft: float
    min_ttft: float


@dataclass
class Latency:
    avg_latency: float
    max_latency: float
    min_latency: float


@dataclass
class Token:
    avg_token: float
    max_token: int
    min_token: int
