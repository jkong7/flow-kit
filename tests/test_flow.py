import json
import os
import tempfile
import unittest

from helpers import BIN, run

FLOW = os.path.join(BIN, "flow")
T0 = 1790000000.0


class FlowTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.cfg = os.path.join(self.home, "cfg")
        self.state = os.path.join(self.home, "state")
        self.env = {"FLOWKIT_CONFIG_DIR": self.cfg, "FLOWKIT_STATE_DIR": self.state, "FLOWKIT_DRY_RUN": "1"}

    def config(self, **cfg):
        os.makedirs(self.cfg, exist_ok=True)
        with open(os.path.join(self.cfg, "flow.json"), "w") as f:
            json.dump(cfg, f)

    def flow(self, *args, at=T0):
        e = dict(self.env, FLOWKIT_NOW=str(at))
        return run(FLOW, args=args, env=e)

    def log(self):
        with open(os.path.join(self.state, "flow-log.jsonl")) as f:
            return [json.loads(l) for l in f]

    def test_start_default_raycast_focus_and_timer(self):
        p = self.flow("start", "25", "OS", "pset")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("raycast://focus/start?goal=OS%20pset&duration=1500&mode=block", p.stdout)
        self.assertIn("DRY: timer 1500s", p.stdout)
        self.assertIn('flow: 25m on "OS pset"', p.stdout)
        self.assertEqual(self.flow("status", at=T0 + 600).stdout.strip(), "⏱ 15m left · OS pset")

    def test_full_config(self):
        self.config(raycast_categories=["social", "news"], focus_on_shortcut="Work On", focus_off_shortcut="Work Off",
                    spotify_playlist="spotify:playlist:abc", open_apps=["Cursor"], open_urls=["https://x.dev"],
                    default_minutes=90, default_goal="Thesis")
        out = self.flow("start").stdout
        self.assertIn("categories=social%2Cnews", out)
        self.assertIn("shortcuts run Work On", out)
        self.assertIn("spotify:playlist:abc", out)
        self.assertIn("open -a Cursor", out)
        self.assertIn("open https://x.dev", out)
        self.assertIn('1h30m on "Thesis"', out)
        out = self.flow("stop", at=T0 + 1800).stdout
        self.assertIn("raycast://focus/complete", out)
        self.assertIn("shortcuts run Work Off", out)
        self.assertIn("pause", out)
        self.assertIn("stopped after 30m", out)

    def test_goal_without_minutes(self):
        p = self.flow("start", "write", "essay")
        self.assertIn('flow: 50m on "write essay"', p.stdout)

    def test_bad_minutes(self):
        self.assertEqual(self.flow("start", "0").returncode, 2)

    def test_raycast_can_be_disabled(self):
        self.config(raycast_focus=False)
        self.assertNotIn("raycast://", self.flow("start").stdout)

    def test_double_start_refused(self):
        self.flow("start")
        p = self.flow("start")
        self.assertEqual(p.returncode, 1)
        self.assertIn("already running", p.stdout)

    def test_timer_end_logs_completed_and_notifies(self):
        self.flow("start", "50", "Resume")
        out = self.flow("_end", at=T0 + 3000).stdout
        self.assertIn("Flow session done", out)
        self.assertIn("Glass.aiff", out)
        entry = self.log()[0]
        self.assertEqual((entry["goal"], entry["actual_min"], entry["completed"]), ("Resume", 50.0, True))
        self.assertEqual(self.flow("status").returncode, 1)
        self.assertEqual(self.flow("status", "-q").stdout, "\n")

    def test_extend(self):
        self.flow("start", "20")
        out = self.flow("extend", "15", at=T0 + 60).stdout
        self.assertIn("+15m, 34m left", out)
        self.assertEqual(self.flow("status", at=T0 + 60).stdout.split()[1], "34m")

    def test_log_summary(self):
        self.flow("start", "50", "OS", at=T0)
        self.flow("_end", at=T0 + 3000)
        self.flow("start", "50", "Jobs", at=T0 + 4000)
        self.flow("stop", at=T0 + 4000 + 1200)
        self.flow("start", "30", "OS", at=T0 + 8000)
        self.flow("_end", at=T0 + 9800)
        out = self.flow("log", at=T0 + 10000).stdout
        self.assertIn("1h40m focused across 3 sessions (2 completed)", out)
        self.assertIn("1h20m  OS", out)
        self.assertIn("20m  Jobs", out)
        self.assertIn("●◐●", out)
        self.assertIn("no sessions", self.flow("log", "--days", "1", at=T0 + 5 * 86400).stdout)

    def test_stop_without_session(self):
        self.assertEqual(self.flow("stop").returncode, 1)

    def test_config_prints_defaults(self):
        out = self.flow("config").stdout
        self.assertIn("not created", out)
        self.assertIn('"default_minutes": 50', out)


if __name__ == "__main__":
    unittest.main()
