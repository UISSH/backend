from subprocess import CompletedProcess


def format_bytes(size) -> (int, str):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0: "", 1: "KB", 2: "MB", 3: "GB", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n]


def format_completed_process(p: CompletedProcess):
    msg = f"result:{p.returncode}\n"
    if p.stdout:
        msg += f"\n{'-' * 10}stdout{'-' * 10}\n"
        msg += p.stdout.decode()
    if p.stderr:
        msg += f"\n{'-' * 10}stderr{'-' * 10}\n"
        msg += p.stderr.decode()
    return msg


def format_os_query_result(data) -> str:
    lines = data.split("\n")
    start_position = 0
    for index, item in enumerate(lines):
        if item.startswith("["):
            start_position = index
            break
    data = "\n".join(lines[start_position:])

    return data
