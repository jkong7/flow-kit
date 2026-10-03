import json
import os
import unittest

from helpers import HOOKS, run

GUARD = os.path.join(HOOKS, "guard_tools.py")


class GuardToolsTest(unittest.TestCase):
    def verdict(self, tool, tool_input=None, env=None):
        p = run(GUARD, {"tool_name": tool, "tool_input": tool_input or {}}, env=env)
        if p.returncode == 2:
            return "deny"
        self.assertEqual(p.returncode, 0, p.stderr)
        if p.stdout.strip():
            return json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"]
        return "allow"

    def test_denies_outbound(self):
        for tool in ["mcp__claude_ai_Gmail__send_message", "mcp__claude_ai_Gmail__forward",
                     "mcp__claude_ai_Gmail__reply", "mcp__claude_ai_Google_Drive__share_file",
                     "mcp__slack__post_message", "mcp__mail__send_email"]:
            with self.subTest(tool=tool):
                self.assertEqual(self.verdict(tool), "deny")

    def test_asks_destructive(self):
        for tool in ["mcp__claude_ai_Gmail__trash_thread", "mcp__claude_ai_Google_Drive__trash_file",
                     "mcp__claude_ai_Google_Calendar__delete_event", "mcp__plugin_todoist_todoist__delete-object",
                     "mcp__claude_ai_Gmail__mark_thread_spam", "mcp__claude_ai_Gmail__delete_label",
                     "mcp__claude_ai_Google_Calendar__respond_to_event"]:
            with self.subTest(tool=tool):
                self.assertEqual(self.verdict(tool), "ask")

    def test_allows_drafts_and_reads(self):
        for tool in ["mcp__claude_ai_Gmail__create_draft", "mcp__claude_ai_Gmail__update_draft",
                     "mcp__claude_ai_Gmail__search_threads", "mcp__claude_ai_Gmail__untrash_message",
                     "mcp__plugin_todoist_todoist__add-tasks", "mcp__plugin_todoist_todoist__reschedule-tasks",
                     "mcp__claude_ai_Notion__notion-send-message-to-session", "Bash", "Write"]:
            with self.subTest(tool=tool):
                self.assertEqual(self.verdict(tool), "allow")

    def test_calendar_invites(self):
        tool = "mcp__claude_ai_Google_Calendar__create_event"
        env = {"FLOWKIT_OWN_EMAILS": "me@x.com, me2@x.com"}
        self.assertEqual(self.verdict(tool, {"summary": "Focus"}, env=env), "allow")
        self.assertEqual(self.verdict(tool, {"attendees": ["me@x.com"]}, env=env), "allow")
        self.assertEqual(self.verdict(tool, {"attendees": [{"email": "prof@nu.edu"}]}, env=env), "ask")
        self.assertEqual(self.verdict(tool, {"attendees": "me2@x.com, rec@co.com"}, env=env), "ask")

    def test_deny_reason_goes_to_stderr(self):
        p = run(GUARD, {"tool_name": "mcp__claude_ai_Gmail__send_message", "tool_input": {}})
        self.assertIn("drafts only", p.stderr)


if __name__ == "__main__":
    unittest.main()
