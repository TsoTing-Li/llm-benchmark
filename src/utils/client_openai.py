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
    error_record: list[dict] | None = None,
) -> tuple[float | None, float | None, int | None]:
    start = time.perf_counter()
    try:
        async with aclient.stream(
            "POST", url=url, headers=headers, json=payload, timeout=timeout
        ) as response:
            if response.status_code == 200:
                first_chunk_received = False
                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: "):
                        data = chunk[6:]
                        if data.strip() == "[DONE]":
                            break

                        try:
                            parsed = orjson.loads(data)
                        except Exception as e:
                            print(f"Chunk parse error: {e}")
                            continue

                        if not first_chunk_received:
                            first_chunk_received = True
                            ttft = time.perf_counter() - start

                        if "usage" in parsed:
                            token = parsed["usage"].get("total_tokens", 0)
                        else:
                            token = None

                latency = time.perf_counter() - start
                return ttft, latency, token
            else:
                if error_record is not None:
                    error_text = await response.aread()
                    error_record.append(
                        {
                            "request": payload,
                            "status": response.status_code,
                            "response": error_text.decode(),
                        }
                    )
                return None, None, None

    except Exception as e:
        print(f"Request failed: {repr(e)}")
        return None, None, None
