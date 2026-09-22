import json
import os
import unittest

from helpers import HOOKS, run

NOTIFY = os.path.join(HOOKS, "notify.py")
DRY = {"FLOWKIT_DRY_RUN": "1"}

class NotifyTest(unittest.TestCase):
    def notify(self, payload, **env):
        e = dict(DRY)
        e.update(env)
        p = run(NOTIFY, payload, env=e)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout

    def test_stop_uses_project_name_and_first_line(self):
        out = self.notify({"hook_event_name": "Stop", "cwd": "/x/my-app",
                           "last_assistant_message": "## Fixed the login bug\n\nDetails..."})
        self.assertIn("Glass.aiff", out)
        self.assertIn("Claude · my-app", out)
        self.assertIn("Fixed the login bug", out)
        self.assertNotIn("##", out)

    def test_permission_prompt_has_distinct_sound(self):
        out = self.notify({"hook_event_name": "Notification", "notification_type": "permission_prompt", "cwd": "/a/b"})
        self.assertIn("Ping.aiff", out)
        self.assertIn("Needs permission", out)

    def test_unknown_notification_type_falls_back(self):
        out = self.notify({"hook_event_name": "Notification", "notification_type": "something_new"})
        self.assertIn("Tink.aiff", out)

    def test_long_message_truncated(self):
        out = self.notify({"hook_event_name": "Stop", "last_assistant_message": "word " * 100})
        line = [l for l in out.splitlines() if "osascript" in l][0]
        self.assertLess(len(json.loads(line[5:])[-1]), 115)

    def test_quotes_are_passed_as_argv_not_script(self):
        out = self.notify({"hook_event_name": "Stop", "last_assistant_message": 'said "hi" & quit'})
        cmd = json.loads([l for l in out.splitlines() if "osascript" in l][0][5:])
        self.assertEqual(cmd[-1], 'said "hi" & quit')
        self.assertTrue(all('"hi"' not in part for part in cmd[:-3]))

    def test_quiet_app_suppresses_banner_but_not_sound(self):
        out = self.notify({"hook_event_name": "Stop"}, FLOWKIT_QUIET_APPS="Terminal, Ghostty",
                          FLOWKIT_FRONT_APP="Terminal")
        self.assertIn("afplay", out)
        self.assertNotIn("osascript", out)

    def test_mute_and_ntfy(self):
        out = self.notify({"hook_event_name": "Stop", "cwd": "/p/app"}, FLOWKIT_MUTE="1",
                          FLOWKIT_NTFY_TOPIC="my-topic")
        self.assertNotIn("afplay", out)
        self.assertIn("https://ntfy.sh/my-topic", out)

    def test_garbage_stdin_never_fails(self):
        p = run(NOTIFY, stdin="not json", env=dict(DRY))
        self.assertEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main()
