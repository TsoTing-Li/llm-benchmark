from dataclasses import dataclass


@dataclass
class Stats:
    started_requests: int = 0
    finished_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    non_200_requests: int = 0
    cancelled_requests: int = 0


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
