#!/usr/bin/env python3
import json
import os
import re
import sys

RULES = [
    (r"(^|_)(send|send_message|send_email|send_mail|forward|forward_message|reply|reply_all|post_message|publish)$", "deny",
     "sends or forwards a message; drafts only, the user sends"),
    (r"(^|_)(share|share_file|add_permission|create_permission|update_permission)$", "deny",
     "shares a file or changes who can see it"),
    (r"(^|_)(mark_\w*spam|update_label|delete_label)$", "ask", "changes mail labels or spam state"),
    (r"(^|_|-)(trash|delete|remove|purge|archive)(_|-|$)", "ask", "deletes, trashes or archives data"),
    (r"(^|_)(respond_to_event)$", "ask", "replies to a calendar invite as the user"),
]

INVITE_TOOLS = re.compile(r"(^|_)(create_event|update_event)$")


def own_emails():
    raw = os.environ.get("FLOWKIT_OWN_EMAILS", "")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def outside_attendees(tool_input):
    attendees = tool_input.get("attendees") or tool_input.get("attendee_emails") or []
    if isinstance(attendees, str):
        attendees = [a for a in re.split(r"[,\s]+", attendees) if a]
    emails = []
    for a in attendees:
        email = a.get("email") if isinstance(a, dict) else a
        if email:
            emails.append(str(email).lower())
    mine = own_emails()
    return [e for e in emails if e not in mine]


def evaluate(tool_name, tool_input):
    if not tool_name.startswith("mcp__"):
        return None
    action = tool_name.rsplit("__", 1)[-1].lower()
    for pattern, verdict, reason in RULES:
        if re.search(pattern, action):
            return verdict, reason
    if INVITE_TOOLS.search(action):
        others = outside_attendees(tool_input or {})
        if others:
            return "ask", "sends a calendar invite to %s" % ", ".join(others[:3])
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    verdict = evaluate(payload.get("tool_name", ""), payload.get("tool_input") or {})
    if not verdict:
        return 0
    action, reason = verdict
    if action == "deny":
        sys.stderr.write("flow-kit guard blocked %s: %s. Leave a draft and tell the user instead.\n"
                         % (payload.get("tool_name"), reason))
        return 2
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": "flow-kit guard: %s" % reason,
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
