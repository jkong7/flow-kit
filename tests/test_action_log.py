import json
import os
import tempfile
import unittest

from helpers import HOOKS, run

LOG = os.path.join(HOOKS, "action_log.py")


class ActionLogTest(unittest.TestCase):
    def setUp(self):
        self.state = tempfile.mkdtemp()
        self.env = {"FLOWKIT_STATE_DIR": self.state, "FLOWKIT_NOW": "2026-10-02T20:30:00"}

    def call(self, tool, tool_input=None):
        p = run(LOG, {"tool_name": tool, "tool_input": tool_input or {}, "session_id": "s1", "cwd": "/x"},
                env=dict(self.env))
        self.assertEqual(p.returncode, 0, p.stderr)

    def entries(self):
        path = os.path.join(self.state, "actions.jsonl")
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return [json.loads(l) for l in f]

    def test_logs_writes_only(self):
        self.call("mcp__claude_ai_Gmail__create_draft", {"to": "a@b.com", "body": "x" * 1000})
        self.call("mcp__claude_ai_Gmail__search_threads", {"q": "x"})
        self.call("mcp__plugin_todoist_todoist__find-tasks", {})
        self.call("mcp__plugin_todoist_todoist__add-tasks", {"tasks": [{"content": "a"}]})
        self.call("Bash", {"command": "ls"})
        got = self.entries()
        self.assertEqual([e["tool"] for e in got],
                         ["mcp__claude_ai_Gmail__create_draft", "mcp__plugin_todoist_todoist__add-tasks"])
        self.assertEqual(got[0]["at"], "2026-10-02T20:30:00")
        self.assertLessEqual(len(got[0]["input"]["body"]), 300)
        self.assertEqual(got[0]["session"], "s1")


if __name__ == "__main__":
    unittest.main()
