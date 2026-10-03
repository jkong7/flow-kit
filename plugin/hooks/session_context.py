#!/usr/bin/env python3
import json
import os
import re
import sys

HANDOFF = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
MAX_CHARS = 1500


def brain_dir():
    return os.path.expanduser(os.environ.get("FLOWKIT_BRAIN", "~/brain"))


def latest_handoff(brain):
    daily = os.path.join(brain, "daily")
    try:
        names = sorted(n for n in os.listdir(daily) if HANDOFF.match(n))
    except FileNotFoundError:
        return None, None
    if not names:
        return None, None
    path = os.path.join(daily, names[-1])
    with open(path) as f:
        return names[-1][:-3], f.read().strip()


def clip(text):
    return text if len(text) <= MAX_CHARS else text[:MAX_CHARS].rsplit("\n", 1)[0] + "\n..."


def build(brain):
    if not os.path.isdir(brain):
        return None
    lines = ["Jonny's second-brain vault is at %s (me/, people/, projects/, classes/, ideas/, decisions/, daily/). "
             "Read the relevant note before asking him something it already answers. Tasks live in Todoist." % brain]
    date, text = latest_handoff(brain)
    if text:
        lines.append("Latest handoff (%s):\n%s" % (date, clip(text)))
    return "\n\n".join(lines)


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    context = build(brain_dir())
    if not context:
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
