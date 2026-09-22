#!/usr/bin/env python3
import json
import os
import re
import shlex
import sys

WRAPPERS = {"sudo", "env", "command", "exec", "nohup", "time", "xargs", "doas"}
DANGER_RM_TARGETS = {"/", "/*", "~", "~/", "~/*", "$HOME", "$HOME/", "$HOME/*", "${HOME}", "..", "../", "../*"}
RISKY_RM_TARGETS = {".", "./", "*", ".*", "./*"}
SYSTEM_DIRS = {"/Users", "/System", "/Library", "/usr", "/etc", "/bin", "/opt", "/Applications", "/private", "/var"}
PROTECTED_BRANCHES = {"main", "master", "production", "prod", "release"}

REGEX_RULES = [
    (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", "deny", "fork bomb"),
    (r"\bmkfs(\.\w+)?\b", "deny", "formats a filesystem"),
    (r"\bdd\b.*\bof=/dev/(r?disk|sd|nvme)", "deny", "writes raw to a disk device"),
    (r"\bdiskutil\s+(erase\w*|zeroDisk|secureErase|partitionDisk)\b", "deny", "erases a disk"),
    (r"\bchmod\s+(-\w*R\w*\s+)?0?777\s+(/|~|\$HOME)(\s|$)", "deny", "world-writable home or root"),
    (r"(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b", "ask", "pipes a download straight into a shell"),
    (r"\bgit\s+reset\s+--hard\b", "ask", "discards uncommitted work"),
    (r"\bgit\s+clean\s+-\w*f", "ask", "deletes untracked files"),
    (r"\bgit\s+(checkout|restore)\s+(--\s+)?\.(\s|$)", "ask", "discards all unstaged changes"),
    (r"\bgit\s+commit\b.*--no-verify", "ask", "skips commit hooks"),
    (r"\bgit\s+branch\s+-D\b", "ask", "force-deletes a branch"),
    (r"\bgit\s+stash\s+(drop|clear)\b", "ask", "drops stashed work"),
    (r"(?i)\b(DROP\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE\s+TABLE)\b", "ask", "destructive SQL"),
    (r"\bgh\s+repo\s+delete\b", "deny", "deletes a GitHub repository"),
    (r"\bgh\s+repo\s+(edit|create)\b.*--visibility[ =]public", "ask", "makes a repository public"),
    (r"\bnpm\s+publish\b|\btwine\s+upload\b|\bcargo\s+publish\b", "ask", "publishes a package"),
    (r"(^|\s)>\s*~?/?\.(zshrc|bashrc|bash_profile|zprofile)\b", "ask", "overwrites a shell rc file"),
    (r"\bsecurity\s+(find|dump)-(generic|internet)-password\b.*-[gw]", "ask", "reads a keychain secret"),
]

SEP = re.compile(r"\|\||&&|;|\||\n|&(?!>)|\$\(|`|\)")


def segments(command):
    for part in SEP.split(command):
        part = part.strip()
        if part:
            yield part


def tokens(segment):
    try:
        toks = shlex.split(segment, comments=True)
    except ValueError:
        toks = segment.split()
    while toks and (toks[0] in WRAPPERS or re.match(r"^\w+=", toks[0]) or (toks[0].startswith("-") and len(toks) > 1)):
        toks = toks[1:]
    return toks


def check_rm(toks, raw):
    if not toks or os.path.basename(toks[0]) != "rm":
        return None
    flags = "".join(t.lstrip("-") for t in toks[1:] if t.startswith("-") and not t.startswith("--"))
    long_flags = {t for t in toks[1:] if t.startswith("--")}
    recursive = "r" in flags or "R" in flags or "--recursive" in long_flags
    force = "f" in flags or "--force" in long_flags
    targets = [t for t in toks[1:] if not t.startswith("-")]
    raw_targets = [t for t in raw.split()[1:] if not t.startswith("-")]
    if not recursive:
        return None
    home = os.path.expanduser("~")
    for t in targets + raw_targets:
        norm = t.rstrip("/") or "/"
        if t in DANGER_RM_TARGETS or norm in DANGER_RM_TARGETS or norm in SYSTEM_DIRS or norm == home:
            return ("deny", "recursive rm of %s" % t)
    for t in targets + raw_targets:
        if t in RISKY_RM_TARGETS:
            return ("ask", "recursive rm of %s%s" % (t, " (forced)" if force else ""))
    return None


def check_push(toks):
    if len(toks) < 2 or os.path.basename(toks[0]) != "git" or "push" not in toks:
        return None
    rest = toks[toks.index("push") + 1:]
    forced = any(t in ("-f", "--force") or (t.startswith("-") and not t.startswith("--") and "f" in t) for t in rest)
    forced = forced or any(t.startswith("+") for t in rest)
    if not forced:
        return None
    refs = [t.lstrip("+") for t in rest if not t.startswith("-")]
    names = set()
    for r in refs[1:] if len(refs) > 1 else refs:
        names.update(r.split(":"))
    if not refs[1:]:
        return ("ask", "force push (branch not named)")
    if names & PROTECTED_BRANCHES:
        return ("deny", "force push to %s" % ", ".join(sorted(names & PROTECTED_BRANCHES)))
    return ("ask", "force push")


def load_extra():
    path = os.environ.get("FLOWKIT_GUARD_RULES")
    if not path:
        return []
    try:
        with open(os.path.expanduser(path)) as f:
            return [(r["pattern"], r.get("action", "ask"), r.get("reason", "custom rule")) for r in json.load(f)]
    except Exception:
        return []


def evaluate(command):
    hits = []
    for seg in segments(command):
        first = seg.split(None, 1)[0] if seg.split() else ""
        if first in ("sudo", "doas"):
            hits.append(("ask", "runs as root"))
        toks = tokens(seg)
        for check in (check_rm(toks, seg), check_push(toks)):
            if check:
                hits.append(check)
    for pattern, action, reason in REGEX_RULES + load_extra():
        if re.search(pattern, command):
            hits.append((action, reason))
    if not hits:
        return None
    deny = [h for h in hits if h[0] == "deny"]
    return deny[0] if deny else hits[0]


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command", "")
    verdict = evaluate(command)
    if not verdict:
        return 0
    action, reason = verdict
    if action == "deny":
        sys.stderr.write("flow-kit guard blocked this command: %s. Ask the user to run it themselves if it is really intended.\n" % reason)
        return 2
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": "flow-kit guard: %s" % reason,
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
