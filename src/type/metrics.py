from dataclasses import dataclass, field, fields


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


@dataclass
class LMCacheRawData:
    num_lookup_hits_total: int = 0
    num_lookup_tokens_total: int = 0
    num_hit_tokens_total: int = 0
    num_retrieve_requests_total: int = 0
    num_store_requests_total: int = 0

    local_cpu_evict_count_total: int = 0


@dataclass
class LMCache:
    raw_data: LMCacheRawData = field(default_factory=LMCacheRawData)

    prefix_hit_ratio: float = 0.0
    retrieve_hit_ratio: float = 0.0
    retrieve_tokens_per_hit: float = 0.0
    evict_ratio: float = 0.0

    def diff(self, baseline: "LMCache") -> "LMCache":
        if baseline is None:
            return None

        new_raw_data = LMCacheRawData()
        for field in fields(LMCacheRawData):
            name = field.name
            setattr(
                new_raw_data,
                name,
                getattr(self.raw_data, name) - getattr(baseline.raw_data, name),
            )

        diff = LMCache(raw_data=new_raw_data)

        diff.prefix_hit_ratio = round(
            (
                new_raw_data.num_lookup_hits_total
                / new_raw_data.num_lookup_tokens_total
                if new_raw_data.num_lookup_tokens_total > 0
                else 0.0
            ),
            2,
        )
        diff.retrieve_hit_ratio = round(
            (
                new_raw_data.num_hit_tokens_total / new_raw_data.num_lookup_tokens_total
                if new_raw_data.num_lookup_tokens_total > 0
                else 0.0
            ),
            2,
        )
        diff.retrieve_tokens_per_hit = round(
            (
                new_raw_data.num_hit_tokens_total
                / new_raw_data.num_retrieve_requests_total
                if new_raw_data.num_retrieve_requests_total > 0
                else 0.0
            ),
            2,
        )
        diff.evict_ratio = round(
            (
                new_raw_data.local_cpu_evict_count_total
                / (
                    new_raw_data.num_store_requests_total
                    + new_raw_data.num_retrieve_requests_total
                )
                if (
                    new_raw_data.num_store_requests_total
                    + new_raw_data.num_retrieve_requests_total
                )
                > 0
                else 0.0
            ),
            2,
        )

        return diff
