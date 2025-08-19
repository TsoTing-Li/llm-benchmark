def text_progress_bar(progress: int, total: int, bar_len: int = 40) -> str:
    filled_len = int(round(bar_len * progress / float(total)))
    bar = "#" * filled_len + "-" * (bar_len - filled_len)
    percent = round(100 * progress / float(total), 1)
    return f"[{bar}] {percent}%"
