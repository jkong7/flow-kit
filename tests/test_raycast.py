import json
import os
import re
import subprocess
import tempfile
import unittest

from helpers import ROOT

RAYCAST = os.path.join(ROOT, "raycast")
SCRIPTS = sorted(f for f in os.listdir(RAYCAST) if f.endswith(".sh"))
MODES = {"silent", "compact", "fullOutput", "inline"}


def headers(path):
    out = {}
    with open(path) as f:
        for line in f:
            m = re.match(r"^# @raycast\.(\w+) (.*)$", line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


class RaycastHeadersTest(unittest.TestCase):
    def test_every_script_is_valid(self):
        self.assertGreaterEqual(len(SCRIPTS), 10)
        titles = set()
        for name in SCRIPTS:
            path = os.path.join(RAYCAST, name)
            with self.subTest(script=name):
                h = headers(path)
                self.assertEqual(h.get("schemaVersion"), "1")
                self.assertIn(h.get("mode"), MODES)
                self.assertTrue(h.get("title"))
                self.assertNotIn(h["title"], titles)
                titles.add(h["title"])
                self.assertTrue(os.access(path, os.X_OK))
                self.assertEqual(subprocess.run(["bash", "-n", path]).returncode, 0)
                for key in ("argument1", "argument2", "argument3"):
                    if key in h:
                        arg = json.loads(h[key])
                        self.assertIn(arg["type"], ("text", "password", "dropdown"))
                        if arg["type"] == "dropdown":
                            self.assertTrue(all("title" in d and "value" in d for d in arg["data"]))
                if h["mode"] == "inline":
                    self.assertIn("refreshTime", h)

    def test_no_comments_besides_raycast_headers(self):
        for name in SCRIPTS:
            with open(os.path.join(RAYCAST, name)) as f:
                lines = f.read().splitlines()
            stray = [l for l in lines[1:] if l.lstrip().startswith("#") and not l.startswith("# @raycast.")]
            self.assertEqual(stray, [], name)


class RaycastRunTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.bin = os.path.join(self.home, "mockbin")
        os.makedirs(self.bin)
        self.clip = os.path.join(self.home, "clip")
        with open(self.clip, "w") as f:
            f.write("clipboard text")
        self.mock("pbpaste", "cat %s" % self.clip)
        self.mock("pbcopy", "cat > /dev/null")
        self.mock("claude", 'cat > /dev/null; echo "CLAUDE $*" | head -c 60')
        self.env = {
            "HOME": self.home,
            "PATH": self.bin + ":/usr/bin:/bin",
            "FLOWKIT_CLAUDE_BIN": os.path.join(self.bin, "claude"),
            "FLOWKIT_INBOX": os.path.join(self.home, "inbox.md"),
            "FLOWKIT_STATE_DIR": os.path.join(self.home, "state"),
            "FLOWKIT_CONFIG_DIR": os.path.join(self.home, "cfg"),
            "FLOWKIT_DRY_RUN": "1",
        }

    def mock(self, name, body):
        p = os.path.join(self.bin, name)
        with open(p, "w") as f:
            f.write("#!/bin/sh\n%s\n" % body)
        os.chmod(p, 0o755)

    def sh(self, name, *args, **env):
        e = dict(self.env)
        e.update(env)
        p = subprocess.run([os.path.join(RAYCAST, name)] + list(args), capture_output=True, text=True, env=e,
                           stdin=subprocess.DEVNULL, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.strip()

    def test_capture_and_inbox(self):
        self.assertEqual(self.sh("inbox.sh"), "Inbox zero")
        self.assertEqual(self.sh("quick-capture.sh", "call mom", FLOWKIT_DRY_RUN="0"), "Captured (1 open)")
        self.assertIn("1 open · oldest:", self.sh("inbox.sh"))
        self.assertIn("call mom", self.sh("inbox.sh"))

    def test_capture_tab(self):
        out = self.sh("capture-tab.sh", "", FLOWKIT_DRY_RUN="0", FLOWKIT_FRONT_TAB="https://a.b\nA B")
        self.assertEqual(out, "Tab captured")
        with open(self.env["FLOWKIT_INBOX"]) as f:
            self.assertIn("[A B](https://a.b)", f.read())

    def test_flow_scripts(self):
        self.assertEqual(self.sh("flow-status.sh"), "")
        self.assertIn('25m on "OS pset"', self.sh("flow-start.sh", "25", "OS pset"))
        self.assertIn("left · OS pset", self.sh("flow-status.sh"))
        self.assertIn("stopped after", self.sh("flow-stop.sh"))

    def test_flow_start_goal_only_and_empty(self):
        self.assertIn('50m on "essay"', self.sh("flow-start.sh", "", "essay"))
        self.sh("flow-stop.sh")
        self.assertIn('50m on "Deep work"', self.sh("flow-start.sh"))

    def test_ai_scripts_call_claude(self):
        self.env["FLOWKIT_DRY_RUN"] = "0"
        self.assertTrue(self.sh("summarize-clipboard.sh").startswith("CLAUDE -p --model haiku"))
        self.assertTrue(self.sh("ask-claude.sh", "what is rust", "none").startswith("CLAUDE -p --model sonnet"))
        self.assertTrue(self.sh("ask-claude.sh", "tl;dr this", "clip").startswith("CLAUDE -p --model sonnet"))
        self.assertTrue(self.sh("draft-reply.sh", "say yes").startswith("CLAUDE -p"))
        self.assertTrue(self.sh("draft-reply.sh").startswith("CLAUDE -p"))


if __name__ == "__main__":
    unittest.main()
