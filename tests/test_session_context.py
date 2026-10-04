import json
import os
import tempfile
import unittest

from helpers import HOOKS, run

HOOK = os.path.join(HOOKS, "session_context.py")


class SessionContextTest(unittest.TestCase):
    def setUp(self):
        self.brain = tempfile.mkdtemp()

    def context(self):
        p = run(HOOK, {"hook_event_name": "SessionStart"}, env={"FLOWKIT_BRAIN": self.brain})
        self.assertEqual(p.returncode, 0, p.stderr)
        if not p.stdout.strip():
            return None
        return json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]

    def write(self, name, text, folder="daily"):
        os.makedirs(os.path.join(self.brain, folder), exist_ok=True)
        with open(os.path.join(self.brain, folder, name), "w") as f:
            f.write(text)

    def test_missing_vault_is_silent(self):
        p = run(HOOK, {}, env={"FLOWKIT_BRAIN": os.path.join(self.brain, "nope")})
        self.assertEqual(p.stdout.strip(), "")

    def test_latest_handoff_wins_and_briefs_are_ignored(self):
        self.write("2026-10-01.md", "# old")
        self.write("2026-10-02.md", "# 2026-10-02\n## Tomorrow first\n- BlackRock OA")
        self.write("2026-10-03-brief.md", "# brief")
        ctx = self.context()
        self.assertIn("Latest handoff (2026-10-02)", ctx)
        self.assertIn("BlackRock OA", ctx)
        self.assertNotIn("# brief", ctx)
        self.assertNotIn("# old", ctx)

    def test_long_handoff_is_capped(self):
        self.write("2026-10-02.md", "\n".join("- line %d" % i for i in range(2000)))
        self.assertLess(len(self.context()), 2200)

    def test_vault_without_handoff_still_points_at_vault(self):
        ctx = self.context()
        self.assertIn(self.brain, ctx)
        self.assertNotIn("Latest handoff", ctx)

    def test_profile_is_loaded_before_handoff(self):
        self.write("profile.md", "# Jonny in one screen\n**Wants to build:** novel consumer AI", folder="me")
        self.write("2026-10-02.md", "# 2026-10-02\n- BlackRock OA")
        ctx = self.context()
        self.assertIn("novel consumer AI", ctx)
        self.assertLess(ctx.index("novel consumer AI"), ctx.index("BlackRock OA"))

    def test_long_profile_is_capped(self):
        self.write("profile.md", "\n".join("- trait %d" % i for i in range(2000)), folder="me")
        self.assertLess(len(self.context()), 3600)

    def test_missing_profile_is_skipped(self):
        self.assertNotIn("Who Jonny is", self.context())


if __name__ == "__main__":
    unittest.main()
