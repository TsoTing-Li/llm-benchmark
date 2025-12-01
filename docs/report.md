### Top level
* **Model server**: The base URL of the model server used for all benchmark requests.
* **Date**: Timestamp indicating when the benchmark was executed, formatted as `YYYYMMDD_HHMMSS`.
* **Stop reason**: The termination reason for the benchmark run (e.g., `done`, `cancelled`, `error`).
* **Run label**: A user-defined label representing the benchmark mode or scenario (e.g.,`single`, `cold`, `warm`)
* **Model**: Model identifier used in the run.
* **Completion type**: The type of completion endpoint used (e.g.,`generate`, `chat`)
* **Limit output tokens**: Max tokens allowed per response.
* **Number of concurrency**: Concurrent workers (simultaneous requests).
* **Duration time**: Total time for the run.
* **Dataset**: Dataset name used for the benchmark.
* **Request per second (req/s)**: Request throughput ~= `Finished requests` / `Duration time`
* **Throughput token (tok/s)**: Average output generation speed (token per second) 

### Stats (Request stat)
* **Started requests**: Total number of requests that were initiated.
* **Finished requests**: Requests that completed processing, regardless of outcome.
* **Successful requests**: Requests that returned 200 OK and completed streaming the response without timeout.
* **Failed requests**: Requests that ended with an error or unexpected exception.
* **Timeout requests**: Requests that exceeded the configured timeout limit.
* **Non-200 requests**: Requests that completed with an HTTP status code other than 200.
* **Cancelled requests**: Requests that were aborted intentionally before completion.

### TTFT (Time To First Token, ms)
* **Avg ttft (ms)**: Average time from request sent to first token received.
* **Max ttft (ms)**: Slowest first token delay observed.
* **Min ttft (ms)**: Fastest first token delay observed.

### Latency (s)
* **Avg latency (s)**: End-to-end time from request sent to last token received (include TTFT and generation).
* **Max latency (s)**: Slowest end-to-end request.
* **Min latency (s)**: Fastest end-to-end request.

### Token (tok/req)
* **Avg token (tok/req)**: Average total tokens per request (input + output).
* **Max token (tok/req)**: Maximum total tokens seen in a request.
* **Min token (tok/req)**: Minimum total tokens seen in a request.

### LMCache Metrics
* **Num lookup hits total**: Total number of tokens hit in lookup from LMCache.
* **Num lookup tokens total**: Total number of tokens requested in lookup from LMCache.
* **Num hit tokens total**: Total number of tokens hit in LMCache.
* **Num retrieve requests total**: Total number of retrieve requests in LMCache.
* **Num store requests total**: Total number of store requests in LMCache.
* **Local CPU evict count total**: Total number of local CPU evict count in LMCache.
* **Prefix hit ratio**: The ratio of tokens successfully found during lookup operations.
* **Retrieve hit ratio**: The ratio of tokens successfully returned by LMCache relative to the total number of tokens requested in lookup.
* **Retrieve tokens per hit**: Average number of tokens retrieved per LMCache hit.
* **Evict ratio**: The ratio of cache entries evicted due to capacity or replacement.