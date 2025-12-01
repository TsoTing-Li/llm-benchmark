from dataclasses import dataclass
from typing import Literal


@dataclass
class Args:
    base_url: str
    endpoint: Literal["/v1/chat/completions", "/v1/completions"]
    api_key: str
    model: str
    concurrency: int
    timeout: int
    prompt: str
    dataset_path: str
    num_request: int
    duration_time: int
    max_tokens: int
    temperature: float
    report_file_root: str
    output_file: str
    use_lmcache_metrics: bool = False
    verbose: bool = False
