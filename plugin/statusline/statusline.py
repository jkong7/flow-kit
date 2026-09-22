#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time

COLOR = os.environ.get("FLOWKIT_STATUS_NO_COLOR") != "1" and os.environ.get("NO_COLOR") is None


def c(code, s):
    return "\033[%sm%s\033[0m" % (code, s) if COLOR else s


DIM, BOLD, GREEN, YELLOW, RED, CYAN, MAGENTA = "2", "1", "32", "33", "31", "36", "35"


def git_info(cwd):
    try:
        out = subprocess.run(["git", "-C", cwd, "status", "--porcelain=v1", "--branch", "--untracked-files=no"],
                             capture_output=True, text=True, timeout=1.5)
    except Exception:
        return None
    if out.returncode != 0:
        return None
    lines = out.stdout.splitlines()
    if not lines:
        return None
    head = lines[0][3:]
    branch = head.split("...")[0].split(" ")[0]
    if branch.startswith("No commits yet on "):
        branch = branch[len("No commits yet on "):]
    if head.startswith("HEAD (no branch)"):
        branch = "detached"
    dirty = len(lines) > 1
    ahead = ""
    if "[ahead " in head:
        ahead = "↑" + head.split("[ahead ")[1].split("]")[0].split(",")[0]
    return branch + ("*" if dirty else "") + ahead


def bar(pct, width=8):
    filled = max(0, min(width, int(round(pct / 100.0 * width))))
    return "▰" * filled + "▱" * (width - filled)


def pct_color(pct, warn=60, crit=80):
    return RED if pct >= crit else YELLOW if pct >= warn else GREEN


def fmt_duration(ms):
    mins = int(ms / 60000)
    return "%dh%02dm" % (mins // 60, mins % 60) if mins >= 60 else "%dm" % mins


def flow_segment(now=None):
    state_dir = os.environ.get("FLOWKIT_STATE_DIR") or os.path.expanduser("~/.local/state/flowkit")
    try:
        with open(os.path.join(state_dir, "session.json")) as f:
            s = json.load(f)
    except Exception:
        return None
    left = int((s.get("ends_at", 0) - (now or time.time())) / 60)
    if left < 0:
        return None
    return c(MAGENTA, "⏱ %dm left" % left)


def render(data, now=None):
    parts = []
    model = (data.get("model") or {}).get("display_name") or "Claude"
    parts.append(c(BOLD, model))

    ws = data.get("workspace") or {}
    cwd = ws.get("current_dir") or data.get("cwd") or os.getcwd()
    name = os.path.basename(cwd.rstrip("/")) or cwd
    loc = c(CYAN, name)
    branch = ws.get("git_worktree") and ("wt:" + ws["git_worktree"]) or git_info(cwd)
    if branch:
        loc += c(DIM, " ⎇ ") + branch
    parts.append(loc)

    ctx = data.get("context_window") or {}
    used = ctx.get("used_percentage")
    if used is not None:
        parts.append("ctx " + c(pct_color(used), "%s %d%%" % (bar(used), used)))

    five = ((data.get("rate_limits") or {}).get("five_hour") or {}).get("used_percentage")
    if five is not None and five >= 50:
        parts.append(c(pct_color(five, 75, 90), "5h %d%%" % five))

    cost = data.get("cost") or {}
    if cost.get("total_cost_usd"):
        parts.append(c(DIM, "$%.2f" % cost["total_cost_usd"]))
    if cost.get("total_duration_ms"):
        parts.append(c(DIM, fmt_duration(cost["total_duration_ms"])))

    flow = flow_segment(now)
    if flow:
        parts.append(flow)
    return c(DIM, " · ").join(parts)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    print(render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
