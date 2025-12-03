# llm-benchmark
### 🚀 Async & OpenAI-Compatible LLM Benchmark
A high-performance benchmarking tool for Large Language Models supporting async execution and OpenAI API format.
Easily measure latency, throughput, and token speed with concurrent requests and streaming response support.
Now also supports LMCache hit-rate analysis, enabling cold/warm run comparison and cache effectiveness evaluation.


## 🏋️ Pre-require
### Docker
* [Docker 20.10+](https://docs.docker.com/engine/install/ubuntu/)
* Setting docker to group
    ```bash
    sudo usermod -aG docker $USER
    ```
### Repository
* clone the repository
  ```bash
  git clone https://github.com/TsoTing-Li/llm-benchmark.git
  ```
## 🛠️ Environment
### Docker
```bash
docker build -f docker/Dockerfile -t llm-benchmark:v0.1.1 .
```

## 🏁 Startup
```bash
docker run -it --rm \
    --name llm-benchmark-tool \
    -v /etc/localtime:/etc/localtime \
    -v $(pwd):/workspace \
    --network=host \
    llm-benchmark:v0.1.1 bash
```

## ✨ Example
### Chat Example
```bash
python3 src/benchmark.py \
    --base_url http://localhost:8000 \
    --endpoint /v1/chat/completions \
    --model google/gemma-3-12b-it \
    --num_request 300 \
    --concurrency 64 \
    --prompt "how are you?" \
    --output_file report.json \
    --max_tokens 32
```
### Generate Example
```bash
python3 src/benchmark.py \
    --base_url http://localhost:8000 \
    --endpoint /v1/completions \
    --model google/gemma-3-12b-it \
    --num_request 300 \
    --concurrency 64 \
    --dataset_path ShareGPT_V3_unfiltered_cleaned_split.json \
    --output_file report.json \
    --max_tokens 32
```
### Using LMCache Metrics

If you want to capture LMCache hit rates, add the `--use_lmcache_metrics` flag to the command.

⚠ **Important:**  
LMCache metrics will only be available if your **model server supports LMCache** and **has LMCache metrics enabled**.  
Currently, **vLLM** is the primary model server that integrates **LMCache**.  
If LMCache metrics are not exposed by the server, the generated reports will not contain any hit-rate information.

When LMCache metrics are available, the tool generates **two separate report files** to help you compare performance differences between **cold** and **warm** runs:

- **Cold Report (`*cold*.json`)**  
  Represents the results from a *cold start*.  
  LMCache is enabled, but because it is the first run, the cache has not been populated yet.  
  This provides a baseline measurement before any cached tokens are available.

- **Warm Report (`*warm*.json`)**  
  Represents the results *after the cache has been populated*, showing performance when LMCache has usable cached tokens.  
  This report reflects the improvements gained from cache hits.


**For more parameter details, please check** [params.md](docs/params.md)

## 📊 Report
* **general content**
  ```json
  {
    "Model server": "http://localhost:8000",
    "Date": "20251128_111225",
    "Stop reason": "done",
    "Run label": "single",
    "Model": "meta-llama/Llama-3.2-3B",
    "Completion type": "generate",
    "Limit output tokens": 32,
    "Number of concurrency": 10,
    "Duration time (s)": 3.35,
    "Dataset": "ShareGPT_V3_unfiltered_cleaned_split.json",
    "Request per second (req/s)": 29.81,
    "Throughput token (tok/s)": 1217.5,
    "Stats": {
      "Started requests": 100,
      "Finished requests": 100,
      "Successful requests": 100,
      "Failed requests": 0,
      "Timeout requests": 0,
      "Non-200 requests": 0,
      "Cancelled requests": 0
    },
    "TTFT": {
      "Avg ttft (ms)": 28.57,
      "Max ttft (ms)": 43.84,
      "Min ttft (ms)": 23.55
    },
    "Latency": {
      "Avg latency (s)": 0.31,
      "Max latency (s)": 0.47,
      "Min latency (s)": 0.02
    },
    "Token": {
      "Avg token (tok/req)": 378.71,
      "Max token (tok/req)": 2697,
      "Min token (tok/req)": 34
    }
  }
  ```
   **if use `--use_lmcache_metrics` flag, the report file will contain below data**
  ```json
  {
    "LMCache Metrics": {
      "Num lookup hits total": 9822,
      "Num lookup tokens total": 9822,
      "Num hit tokens total": 1932,
      "Prefix hit ratio": 1.0,
      "Retrieve hit ratio": 0.2,
    }
  }
  ```
- **For more report detail, please check** [report.md](docs/report.md)
