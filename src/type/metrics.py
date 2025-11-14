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
    avg_ttft: float | None
    max_ttft: float | None
    min_ttft: float | None


@dataclass
class Latency:
    avg_latency: float | None
    max_latency: float | None
    min_latency: float | None


@dataclass
class Token:
    avg_token: float | None
    max_token: int | None
    min_token: int | None
