import json
import os
import re
import subprocess
import tempfile
import unittest

from helpers import ROOT, run

STATUS = os.path.join(ROOT, "plugin", "statusline", "statusline.py")
ANSI = re.compile(r"\033\[[0-9;]*m")


def sample(**over):
    data = {
        "model": {"id": "claude-opus-5", "display_name": "Opus"},
        "workspace": {"current_dir": "/nonexistent/my-proj"},
        "context_window": {"used_percentage": 38},
        "cost": {"total_cost_usd": 0.4212, "total_duration_ms": 12 * 60000},
        "rate_limits": {"five_hour": {"used_percentage": 23.5}},
    }
    data.update(over)
    return data


class StatuslineTest(unittest.TestCase):
    def render(self, data, **env):
        p = run(STATUS, data, env=env)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.strip()

    def plain(self, data, **env):
        return ANSI.sub("", self.render(data, **env))

    def test_basic_segments(self):
        out = self.plain(sample())
        self.assertEqual(out, "Opus · my-proj · ctx ▰▰▰▱▱▱▱▱ 38% · $0.42 · 12m")

    def test_rate_limit_shown_when_high(self):
        out = self.plain(sample(rate_limits={"five_hour": {"used_percentage": 81}}))
        self.assertIn("5h 81%", out)

    def test_context_color_thresholds(self):
        self.assertIn("\033[32m", self.render(sample(context_window={"used_percentage": 10})))
        self.assertIn("\033[33m", self.render(sample(context_window={"used_percentage": 65})))
        self.assertIn("\033[31m", self.render(sample(context_window={"used_percentage": 90})))

    def test_no_color(self):
        self.assertNotIn("\033[", self.render(sample(), FLOWKIT_STATUS_NO_COLOR="1"))

    def test_git_branch_and_dirty(self):
        d = tempfile.mkdtemp()
        g = ["git", "-C", d]
        subprocess.run(g + ["init", "-q", "-b", "feat"], check=True)
        subprocess.run(g + ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x"], check=True)
        out = self.plain(sample(workspace={"current_dir": d}))
        self.assertIn("⎇ feat", out)
        self.assertNotIn("feat*", out)
        with open(os.path.join(d, "f"), "w") as f:
            f.write("x")
        subprocess.run(g + ["add", "f"], check=True)
        self.assertIn("⎇ feat*", self.plain(sample(workspace={"current_dir": d})))

    def test_worktree_label(self):
        out = self.plain(sample(workspace={"current_dir": "/x/y", "git_worktree": "fix-login"}))
        self.assertIn("⎇ wt:fix-login", out)

    def test_flow_session_segment(self):
        state = tempfile.mkdtemp()
        import time
        with open(os.path.join(state, "session.json"), "w") as f:
            json.dump({"goal": "x", "ends_at": time.time() + 31 * 60 + 5}, f)
        out = self.plain(sample(), FLOWKIT_STATE_DIR=state)
        self.assertTrue(out.endswith("⏱ 31m left"), out)

    def test_empty_input(self):
        self.assertTrue(self.plain({}).startswith("Claude · "))

    def test_long_duration(self):
        self.assertIn("1h05m", self.plain(sample(cost={"total_duration_ms": 65 * 60000})))


if __name__ == "__main__":
    unittest.main()
