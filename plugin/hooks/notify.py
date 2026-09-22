#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import urllib.request

EVENTS = {
    ("Stop", None): ("Done", "Glass"),
    ("SubagentStop", None): ("Subagent done", "Pop"),
    ("Notification", "permission_prompt"): ("Needs permission", "Ping"),
    ("Notification", "idle_prompt"): ("Waiting for you", "Tink"),
    ("Notification", "elicitation_dialog"): ("Has a question", "Purr"),
    ("Notification", "agent_needs_input"): ("Agent needs input", "Purr"),
    ("Notification", None): ("Notification", "Tink"),
}

DRY = os.environ.get("FLOWKIT_DRY_RUN") == "1"


def classify(payload):
    event = payload.get("hook_event_name", "")
    ntype = payload.get("notification_type")
    return EVENTS.get((event, ntype)) or EVENTS.get((event, None)) or ("Claude", "Tink")


def summarize(payload, label):
    text = payload.get("last_assistant_message") or payload.get("message") or ""
    line = next((l.strip() for l in text.splitlines() if l.strip()), "")
    line = line.lstrip("#*-> ").strip()
    if len(line) > 110:
        line = line[:107].rstrip() + "..."
    return line or label


def front_app():
    if "FLOWKIT_FRONT_APP" in os.environ:
        return os.environ["FLOWKIT_FRONT_APP"]
    try:
        asn = subprocess.run(["lsappinfo", "front"], capture_output=True, text=True, timeout=1).stdout.strip()
        out = subprocess.run(["lsappinfo", "info", "-only", "name", asn],
                             capture_output=True, text=True, timeout=1).stdout
        return out.split("=", 1)[1].strip().strip('"') if "=" in out else ""
    except Exception:
        return ""


def run(cmd):
    if DRY:
        print("DRY:", json.dumps(cmd, ensure_ascii=False))
        return
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def banner(title, subtitle, message, sound):
    script = [
        "on run argv",
        "display notification (item 3 of argv) with title (item 1 of argv) subtitle (item 2 of argv)",
        "end run",
    ]
    cmd = ["osascript"]
    for line in script:
        cmd += ["-e", line]
    run(cmd + [title, subtitle, message])


def play(sound):
    run(["afplay", "/System/Library/Sounds/%s.aiff" % sound])


def ntfy(topic, title, message, event):
    url = os.environ.get("FLOWKIT_NTFY_URL", "https://ntfy.sh").rstrip("/") + "/" + topic
    headers = {"Title": title, "Tags": "robot" if event == "Stop" else "warning",
               "Priority": "default" if event == "Stop" else "high"}
    if DRY:
        print("DRY: ntfy", url, json.dumps(headers, ensure_ascii=False), json.dumps(message, ensure_ascii=False))
        return
    try:
        req = urllib.request.Request(url, data=message.encode(), headers=headers, method="POST")
        urllib.request.urlopen(req, timeout=4).read()
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    label, sound = classify(payload)
    project = os.path.basename((payload.get("cwd") or os.getcwd()).rstrip("/")) or "Claude"
    title = "Claude · %s" % project
    message = summarize(payload, label)

    if os.environ.get("FLOWKIT_MUTE") != "1":
        play(sound)
    quiet = [a.strip().lower() for a in os.environ.get("FLOWKIT_QUIET_APPS", "").split(",") if a.strip()]
    if not quiet or front_app().lower() not in quiet:
        banner(title, label, message, sound)
    topic = os.environ.get("FLOWKIT_NTFY_TOPIC")
    if topic:
        ntfy(topic, "%s: %s" % (title, label), message, payload.get("hook_event_name"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
