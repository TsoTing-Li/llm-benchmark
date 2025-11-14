### Top level
* `Date`: Execute date.
* `Model`: Model identifier used in the run.
* `Limit output tokens`: Max tokens allowed per response.
* `Number of concurrency`: Concurrent workers (simultaneous requests).
* `Duration time`: Total time for the run.
* `Dataset`: Dataset name used for the benchmark.
* `Request per second (req/s)`: Request throughput ~= `Finished requests` / `Duration time`
* `Throughput token (tok/s)`: Average output generation speed (token per second) 

### Stats (Request stat)
* `Started requests`: Total number of requests that were initiated.
* `Finished requests`: Requests that completed processing, regardless of outcome.
* `Successful requests`: Requests that returned 200 OK and completed streaming the response without timeout.
* `Failed requests`: Requests that ended with an error or unexpected exception.
* `Timeout requests`: Requests that exceeded the configured timeout limit.
* `Non-200 requests`: Requests that completed with an HTTP status code other than 200.
* `Cancelled requests`: Requests that were aborted intentionally before completion.

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