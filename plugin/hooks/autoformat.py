#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys

PRETTIER_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json", ".css", ".scss",
                ".html", ".vue", ".svelte", ".yaml", ".yml", ".graphql"}

FORMATTERS = {
    ".py": [["ruff", "format", "--quiet"], ["black", "--quiet"]],
    ".go": [["gofmt", "-w"]],
    ".rs": [["rustfmt", "--edition", "2021"]],
    ".sh": [["shfmt", "-w"]],
    ".bash": [["shfmt", "-w"]],
    ".swift": [["swift-format", "--in-place"], ["swiftformat", "--quiet"]],
    ".lua": [["stylua"]],
    ".tf": [["terraform", "fmt"]],
}
for ext in PRETTIER_EXT:
    FORMATTERS[ext] = [["biome", "format", "--write"], ["prettier", "--write", "--log-level", "silent"]]


def find_bin(name, start):
    d = os.path.abspath(start)
    while True:
        for sub in ("node_modules/.bin", ".venv/bin", "venv/bin"):
            cand = os.path.join(d, sub, name)
            if os.access(cand, os.X_OK):
                return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return shutil.which(name)


def pick(path):
    ext = os.path.splitext(path)[1].lower()
    for cand in FORMATTERS.get(ext, []):
        exe = find_bin(cand[0], os.path.dirname(path))
        if exe:
            return [exe] + cand[1:] + [path]
    return None


def main():
    if os.environ.get("FLOWKIT_FORMAT_OFF") == "1":
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        return 0
    if not os.path.isabs(path):
        path = os.path.join(payload.get("cwd") or os.getcwd(), path)
    if not os.path.isfile(path):
        return 0
    cmd = pick(path)
    if not cmd:
        return 0
    if os.environ.get("FLOWKIT_DRY_RUN") == "1":
        print("DRY:", json.dumps(cmd))
        return 0
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
