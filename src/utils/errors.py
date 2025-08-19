import json

from anyio import open_file


async def save_error_as_file(error_data: list[dict], path: str = "error.jsonl") -> None:
    async with await open_file(path, "w") as f:
        for entry in error_data:
            line = json.dumps(entry) + "\n"
            await f.write(line)
