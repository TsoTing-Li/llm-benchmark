import re

import httpx

from type.metrics import LMCache, LMCacheRawData


def parse_lmcache_metrics_response(
    metrics_data: str,
) -> dict[str, list[dict[str, dict[str, str] | float]]]:
    metrics = {}
    pattern = re.compile(
        r"^([a-zA-Z_:][a-zA-Z0-9_:]*)"  # metric name
        r"(?:\{([^}]*)\})?"  # optional labels
        r"\s+([0-9.eE+-]+)$"  # metric value
    )

    for line in metrics_data.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        match = pattern.match(line)
        if not match:
            continue

        name, label_str, value = match.groups()

        # Parse labels into dict
        labels = {}
        if label_str:
            for kv in label_str.split(","):
                k, v = kv.split("=", 1)
                labels[k.strip()] = v.strip().strip('"')

        # Convert numeric value
        try:
            value = float(value)
        except ValueError:
            pass

        # Save result
        metrics.setdefault(name, []).append(
            {
                "labels": labels,
                "value": value,
            }
        )

    return metrics


def fetch_lmcache_metrics(
    lmcache_host: str,
) -> dict[str, list[dict[str, dict[str, str] | float]]] | None:
    try:
        with httpx.Client() as client:
            timeout_cfg = httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=5.0)
            response = client.get(f"{lmcache_host}:7000/metrics", timeout=timeout_cfg)
            response.raise_for_status()

            metrics_data = response.text

    except httpx.HTTPError:
        print(
            f"\n❌ Failed to get LMCache metrics from model-server {lmcache_host}",
            flush=True,
        )
        return None

    try:
        metrics = parse_lmcache_metrics_response(metrics_data)
        return metrics

    except Exception as e:
        print(f"\n❌ Failed to parse LMCache metrics: {e}", flush=True)
        return None


def get_metrics_value(
    metrics: dict[str, list[dict[str, dict[str, str] | float]]], metric_name: str
) -> float | None:
    metric_entries = metrics.get(metric_name, [])
    if len(metric_entries) > 0:
        return metric_entries[0].get("value", 0)
    return 0


def get_lmcache_metrics(lmcache_host: str) -> LMCache | None:
    metrics = fetch_lmcache_metrics(lmcache_host=lmcache_host)
    if metrics is not None:
        num_lookup_hits_total = get_metrics_value(
            metrics, "lmcache:num_lookup_hits_total"
        )
        num_lookup_tokens_total = get_metrics_value(
            metrics, "lmcache:num_lookup_tokens_total"
        )
        num_hit_tokens_total = get_metrics_value(
            metrics, "lmcache:num_hit_tokens_total"
        )
        num_retrieve_requests_total = get_metrics_value(
            metrics, "lmcache:num_retrieve_requests_total"
        )
        num_store_requests_total = get_metrics_value(
            metrics, "lmcache:num_store_requests_total"
        )

        local_cpu_evict_count_total = get_metrics_value(
            metrics, "lmcache:local_cpu_evict_count_total"
        )

        raw_data = LMCacheRawData(
            num_lookup_hits_total=int(num_lookup_hits_total),
            num_lookup_tokens_total=int(num_lookup_tokens_total),
            num_hit_tokens_total=int(num_hit_tokens_total),
            num_retrieve_requests_total=int(num_retrieve_requests_total),
            num_store_requests_total=int(num_store_requests_total),
            local_cpu_evict_count_total=int(local_cpu_evict_count_total),
        )

        prefix_hit_ratio = (
            raw_data.num_lookup_hits_total / raw_data.num_lookup_tokens_total
            if raw_data.num_lookup_tokens_total > 0
            else 0.0
        )
        retrieve_hit_ratio = (
            raw_data.num_hit_tokens_total / raw_data.num_lookup_tokens_total
            if raw_data.num_lookup_tokens_total > 0
            else 0.0
        )
        retrieve_tokens_per_hit = (
            raw_data.num_hit_tokens_total / raw_data.num_retrieve_requests_total
            if raw_data.num_retrieve_requests_total > 0
            else 0.0
        )
        evict_ratio = (
            raw_data.local_cpu_evict_count_total
            / (raw_data.num_store_requests_total + raw_data.num_retrieve_requests_total)
            if (
                raw_data.num_store_requests_total + raw_data.num_retrieve_requests_total
            )
            > 0
            else 0.0
        )

        lmcache_metrics = LMCache(
            raw_data=raw_data,
            prefix_hit_ratio=round(prefix_hit_ratio, 2),
            retrieve_hit_ratio=round(retrieve_hit_ratio, 2),
            retrieve_tokens_per_hit=round(retrieve_tokens_per_hit, 2),
            evict_ratio=round(evict_ratio, 2),
        )
        return lmcache_metrics

    return None
