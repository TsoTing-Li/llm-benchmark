import itertools
import os
from typing import Iterator

import orjson
from anyio import open_file


async def read_dataset_file(path: str) -> dict[str, str]:
    prompts: dict[str, str] = dict()

    async with await open_file(path) as f:
        contents = await f.read()

    try:
        dec_contents = orjson.loads(contents)
    except orjson.JSONDecodeError:
        raise RuntimeError("JSON decode error") from None

    for data in dec_contents:
        if len(data["conversations"]) == 0:
            continue
        prompts.update({data["id"]: data["conversations"][0]["value"]})

    return prompts


async def build_dataset(path: str, prompt: str) -> Iterator[str]:
    if os.path.isfile(path):
        datasets = await read_dataset_file(path=path)
        datasets_cycle = itertools.cycle(datasets.values())

    else:
        datasets_cycle = itertools.cycle([prompt])

    return datasets_cycle
