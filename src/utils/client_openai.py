import asyncio
import math
import time
from typing import Literal

import httpx
import orjson

from type.run_args import Args


def build_payload(
    completion_type: Literal["chat", "generate"], prompt: str, args: Args
) -> dict:
    if completion_type == "chat":
        return {
            "model": args.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": args.temperature,
            "max_completion_tokens": args.max_tokens,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
    elif completion_type == "generate":
        return {
            "model": args.model,
            "prompt": prompt,
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "stream": True,
            "stream_options": {"include_usage": True},
        }


async def request_openai_format(
    aclient: httpx.AsyncClient,
    url: str,
    headers: dict,
    payload: dict,
    timeout: int,
) -> tuple[float | None, float | None, int | None]:
    try:
        timeout_cfg = httpx.Timeout(connect=10.0, read=None, write=60.0, pool=10.0)
        async with asyncio.timeout(timeout):
            start = time.perf_counter()
            token = 0
            ttft = math.inf
            buffer = ""

            async with aclient.stream(
                "POST", url=url, headers=headers, json=payload, timeout=timeout_cfg
            ) as response:
                if response.status_code == 200:
                    first_chunk_received = False
                    async for chunk in response.aiter_lines():
                        if not chunk.startswith("data: "):
                            continue

                        data = chunk[6:]
                        if data.strip() == "[DONE]":
                            break

                        buffer += data
                        try:
                            parsed = orjson.loads(buffer)
                            buffer = ""
                        except Exception:
                            continue

                        if not first_chunk_received:
                            first_chunk_received = True
                            ttft = time.perf_counter() - start

                        usage = parsed.get("usage")
                        if usage is not None and "total_tokens" in usage:
                            token = usage.get("total_tokens")
                            break

                    latency = time.perf_counter() - start
                    return ttft if not math.isinf(ttft) else latency, latency, token
                else:
                    try:
                        error_text = await response.aread()
                        error = orjson.loads(error_text)
                        error_message = error["error"]["message"]
                    except Exception:
                        error_message = "Failed to get error message"
                    raise httpx.HTTPStatusError(
                        f"{error_message}",
                        request=response.request,
                        response=response,
                    )

    except httpx.ConnectTimeout:
        raise

    except httpx.WriteTimeout:
        raise

    except httpx.PoolTimeout:
        raise

    except asyncio.TimeoutError:
        raise

    except httpx.HTTPStatusError as e:
        raise httpx.HTTPStatusError(
            f"{e}",
            request=e.request,
            response=e.response,
        ) from None

    except Exception as e:
        raise Exception(f"Request failed: {repr(e)}") from None
