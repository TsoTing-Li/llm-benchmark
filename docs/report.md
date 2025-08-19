### Top level
* `Model`: Model identifier used in the run.
* `Limit output tokens`: Max tokens allowed per response.
* `Number of concurrency`: Concurrent workers (simultaneous requests).
* `Total requests`: Total requests for the run.
* `Duration time`: Total time for the run.
* `Dataset`: Dataset name used for the benchmark.
* `Successful requests`: Count of requests that returned valid responses.
* `Request per second (req/s)`: Request throughput ~= `Successful requests` / `Duration time`
* `Throughput token (tok/s)`: Average output generation speed (token per second) 

### TTFT (Time To First Token, ms)
* `Avg ttft (ms)`: Average time from request sent to first token received.
* `Max ttft (ms)`: Slowest first token delay observed.
* `Min ttft (ms)`: Fastest first token delay observed.

### Latency (s)
* `Avg latency (s)`: End-to-end time from request sent to last token received (include TTFT and generation).
* `Max latency (s)`: Slowest end-to-end request.
* `Min latency (s)`: Fastest end-to-end request.

### Token (tok/req)
* `Avg token (tok/req)`: Average total tokens per request (input + output).
* `Max token (tok/req)`: Maximum total tokens seen in a request.
* `Min token (tok/req)`: Minimum total tokens seen in a request.