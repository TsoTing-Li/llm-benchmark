## Parameters Description

| param | type | description | example | require/default |
| :---: | :---: | :---: | :-----------: | :-------: |
| base_url | str  | Base API URL | http://localhost:8000, https://api.openai.com | **Required**
| endpoint | str  | API path (allowed: `/v1/chat/completions` or `/v1/completions`). | `/v1/chat/completions`, `/v1/completions` | **Optional**<br>default: `/v1/chat/completions`
| api_key | str  | Include only if your model server requires auth | `sk-...`  | **Optional**<br>default: None
| model | str  |Model name or ID | `gpt-4o-mini`, `llama3-8b` |  **Required**
| num_request | int  | Total requests (exclusive with `duration_time`) | `1000`  | **Optional**<br>default: 100
| duration_time | int  | Test length in seconds (exclusive with `num_request`) | `60`  | **Optional**<br>default: 0
| concurrency | int  | Number of concurrent workers (simultaneous requests).  | `16`  | **Optional**<br>default: 16
| timeout | int  | Per-request timeout.  | `30` | **Optional**<br>default: 30
| prompt | str  | Single-case input; used when `dataset_path` is omitted (iterated) | `how are you?`  | **Optional**<br>default: how are you?
| dataset_path | str  | Batch dataset path (only support ShareGPT format); if absent, `prompt` is reused | `./ShareGPT_V3_unfiltered_cleaned_split.json` | **Optional**<br>
| output_file | str  | Report output path | `./report.json` | **Optional**<br>default: ./report.json
| max_tokens | int  | Maximum tokens to generate per response.  | `256`  | **Optional**<br>default: 32
| temperature | float  | Sampling temperature (higher = more random; 0 ≈ greedy).  | 0.7、0.0  | **Optional**<br>default: 0.7