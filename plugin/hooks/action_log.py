#!/usr/bin/env python3
import datetime
import json
import os
import re
import sys

READ_ONLY = re.compile(r"^(find|get|list|search|read|fetch|query|view|export|user[-_]info|analyze|suggest|resolve|tabs[-_]context|read[-_]page|get[-_]page[-_]text)")
MAX_FIELD = 300


def log_path():
    state = os.environ.get("FLOWKIT_STATE_DIR") or os.path.expanduser("~/.local/state/flowkit")
    return os.path.join(state, "actions.jsonl")


def now():
    return os.environ.get("FLOWKIT_NOW") or datetime.datetime.now().isoformat(timespec="seconds")


def clip(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= MAX_FIELD else text[:MAX_FIELD - 3] + "..."


def summarize_input(tool_input):
    return {k: clip(v) for k, v in (tool_input or {}).items()}


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    name = payload.get("tool_name", "")
    if not name.startswith("mcp__"):
        return 0
    action = name.rsplit("__", 1)[-1]
    if READ_ONLY.match(action.lower()):
        return 0
    entry = {
        "at": now(),
        "session": payload.get("session_id"),
        "cwd": payload.get("cwd"),
        "tool": name,
        "input": summarize_input(payload.get("tool_input")),
    }
    path = log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
