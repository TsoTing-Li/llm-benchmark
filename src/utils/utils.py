import tqdm


def verbose_log(msg: str, pbar: tqdm.tqdm | None, verbose: bool) -> None:
    if not verbose:
        return

    if pbar is not None:
        tqdm.tqdm.write(msg)
    else:
        print(msg, flush=True)
