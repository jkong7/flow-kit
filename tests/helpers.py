import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "plugin", "hooks")
BIN = os.path.join(ROOT, "bin")


def run(script, payload=None, args=(), env=None, stdin=None):
    home = env.pop("HOME") if env and "HOME" in env else tempfile.mkdtemp()
    full_env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": home,
        "FLOWKIT_CONFIG_DIR": os.path.join(home, ".config", "flowkit"),
        "FLOWKIT_STATE_DIR": os.path.join(home, ".local", "state", "flowkit"),
        "FLOWKIT_INBOX": os.path.join(home, "inbox.md"),
    }
    full_env.update(env or {})
    if payload is not None:
        stdin = json.dumps(payload)
    return subprocess.run([sys.executable, script] + list(args), input=stdin or "",
                          capture_output=True, text=True, env=full_env, timeout=30)
