"""
Parse log lines; collect error lines grouped by error code.
Time: O(n), Space: O(k + m) where k = error codes, m = error lines stored.
"""
from typing import List, Dict

def parse_errors(log_lines: List[str]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}
    for line in log_lines:
        # Fast path: must contain "ERROR "
        if "ERROR " not in line:
            continue
        # Find error code token that looks like EXYZ (E + digits or alnum)
        # Avoid heavy regex; do simple token scan.
        # Split once around "ERROR " to reduce scanning.
        try:
            _, after = line.split("ERROR ", 1)
        except ValueError:
            continue
        # error code is first token in 'after', strip punctuation like ":"
        after = after.lstrip()
        if not after:
            continue
        # extract token until space or colon
        code = []
        for ch in after:
            if ch.isalnum() or ch == "_":
                code.append(ch)
            else:
                break
        code = "".join(code)
        if not code or not code.startswith("E"):
            continue
        groups.setdefault(code, []).append(line.rstrip("\n"))
    return groups
