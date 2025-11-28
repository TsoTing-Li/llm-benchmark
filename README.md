# llm-benchmark
### 🚀 Async & OpenAI-Compatible LLM Benchmark
A high-performance benchmarking tool for Large Language Models supporting async execution and OpenAI API format.
Easily measure latency, throughput, and token speed with concurrent requests and streaming response support. Perfect for evaluating both cloud and self-hosted models.

## 🏋️ Pre-require
* Docker
    * [Docker 20.10+](https://docs.docker.com/engine/install/ubuntu/)
    * Setting docker to group
        ```bash
        sudo usermod -aG docker $USER
        ```
* Repository
    * clone the repository
      ```bash
      git clone https://github.com/TsoTing-Li/llm-benchmark.git
      ```
## 🛠️ Build environment in docker
```bash
docker build -f docker/Dockerfile -t llm-benchmark:v0.1.0 .
```

## 🏁 Startup
```bash
docker run -it --rm --name llm-benchmark-tool -v $(pwd):/workspace llm-benchmark bash
```

## ✨ Example
* chat example
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
* generate example
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
- **For more parameter details, please check** [params.md](docs/params.md)

## 📊 Report

```json
{
  "Date": "20251114_111225",
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
- **For more report detail, please check** [report.md](docs/report.md)
