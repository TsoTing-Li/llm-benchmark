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
## 🛠️ Build environment in docker
```bash
docker build -f docker/Dockerfile -t innodiskorg/llm-benchmark:latest .
```

## 🏁 Startup
```bash
docker run -it --rm --name llm-benchmark-tool -v $(pwd):/workspace innodiskorg/llm-benchmark bash
```

## ✨ Example
* chat example
    ```bash
    python3 src/benchmark.py \
        --base_url http://locahost:8000 \
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
        --base_url http://locahost:8000 \
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
  "Model": "google/gemma-3-12b-it",
  "Limit output tokens": 32,
  "Number of concurrency": 64,
  "Total requests": 300,
  "Duration time (s)": 33.36,
  "Dataset": "ShareGPT_V3_unfiltered_cleaned_split.json",
  "Successful requests": 300,
  "Request per second (req/s)": 8.99,
  "Throughput token (tok/s)": 63.73,
  "TTFT": {
    "Avg ttft (ms)": 1494.08,
    "Max ttft (ms)": 6533.24,
    "Min ttft (ms)": 80.89
  },
  "Latency": {
    "Avg latency (s)": 6.97,
    "Max latency (s)": 11.82,
    "Min latency (s)": 1.51
  },
  "Token": {
    "Avg token (tok/req)": 444.1,
    "Max token (tok/req)": 5783,
    "Min token (tok/req)": 24
  }
}
```
- **For more report detail, please check** [report.md](docs/report.md)
