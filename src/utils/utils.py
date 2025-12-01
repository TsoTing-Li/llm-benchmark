import re

import tqdm


def verbose_log(msg: str, pbar: tqdm.tqdm | None, verbose: bool) -> None:
    if not verbose:
        return

    if pbar is not None:
        tqdm.tqdm.write(msg)
    else:
        print(msg, flush=True)


def extract_ip_from_url(url: str) -> str | None:
    pattern = r"^(https?://)((?:\d{1,3}\.){3}\d{1,3})"

    match = re.match(pattern, url)
    if match:
        return match.group(1) + match.group(2)
    return None
