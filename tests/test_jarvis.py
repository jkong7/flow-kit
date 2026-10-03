import os
import tempfile
import unittest

from helpers import BIN, run

JARVIS = os.path.join(BIN, "jarvis")


class JarvisTest(unittest.TestCase):
    def setUp(self):
        self.brain = tempfile.mkdtemp()
        self.state = tempfile.mkdtemp()
        self.env = {"FLOWKIT_BRAIN": self.brain, "FLOWKIT_STATE_DIR": self.state}

    def call(self, *args, **env):
        e = dict(self.env)
        e.update(env)
        return run(JARVIS, args=args, env=e)

    def test_capture_writes_inbox_file(self):
        p = self.call("capture", "remind me to email Professor Tse Monday")
        self.assertEqual(p.returncode, 0, p.stderr)
        path = p.stdout.strip()
        self.assertTrue(path.startswith(os.path.join(self.brain, "inbox")))
        self.assertIn("remind-me-to-email-professor-tse", path)
        with open(path) as f:
            body = f.read()
        self.assertTrue(body.startswith("remind me to email Professor Tse Monday\n"))
        self.assertIn("Source: voice", body)

    def test_ask_dry_run_does_not_call_claude(self):
        p = self.call("ask", "what's", "due", "today", FLOWKIT_DRY_RUN="1", FLOWKIT_CLAUDE_BIN="/bin/echo")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("DRY:", p.stdout)

    def test_toggle_dry_run_starts_recording(self):
        p = self.call("toggle", FLOWKIT_DRY_RUN="1")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("avfoundation", p.stdout)


if __name__ == "__main__":
    unittest.main()
