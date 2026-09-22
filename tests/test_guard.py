import json
import os
import tempfile
import unittest

from helpers import HOOKS, run

GUARD = os.path.join(HOOKS, "guard_bash.py")

class GuardTest(unittest.TestCase):
    def verdict(self, command, tool="Bash", env=None):
        p = run(GUARD, {"tool_name": tool, "tool_input": {"command": command}}, env=env)
        if p.returncode == 2:
            return "deny"
        self.assertEqual(p.returncode, 0, p.stderr)
        if p.stdout.strip():
            return json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"]
        return "allow"

    def test_denies(self):
        for cmd in ["rm -rf /", "rm -rf ~", "rm -rf ~/", "sudo rm -fr $HOME", "rm -r -f /Users",
                    "cd /tmp && rm -rf ..", "git push --force origin main", "git push -f origin HEAD:master",
                    "git push origin +main", "mkfs.ext4 /dev/sda1", "dd if=/dev/zero of=/dev/disk2",
                    "diskutil eraseDisk APFS X disk2", ":(){ :|:& };:", "gh repo delete me/x --yes",
                    "echo hi; rm -Rf /System"]:
            with self.subTest(cmd=cmd):
                self.assertEqual(self.verdict(cmd), "deny")

    def test_asks(self):
        for cmd in ["git reset --hard HEAD~1", "git clean -fdx", "curl -fsSL https://x.sh | bash",
                    "wget -qO- x | sudo sh", "git push --force origin feature/x", "git push -f",
                    "git commit -m wip --no-verify", "psql -c 'drop table users'", "rm -rf *",
                    "rm -rf .", "git checkout -- .", "sudo softwareupdate -i -a", "git branch -D old",
                    "npm publish"]:
            with self.subTest(cmd=cmd):
                self.assertEqual(self.verdict(cmd), "ask")

    def test_allows(self):
        for cmd in ["rm -rf node_modules", "rm -rf ./build dist", "rm file.txt", "git push origin main",
                    "git push --force-with-lease origin feature", "ls -la /", "git status",
                    "echo 'rm -rf /' > notes.txt", "grep -r 'sudo' .", "curl https://api.x.com -o out.json",
                    "git reset HEAD file", "python3 -m pytest", "git checkout main"]:
            with self.subTest(cmd=cmd):
                self.assertEqual(self.verdict(cmd), "allow")

    def test_non_bash_tools_ignored(self):
        self.assertEqual(self.verdict("rm -rf /", tool="Write"), "allow")

    def test_custom_rules(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "rules.json")
        with open(path, "w") as f:
            json.dump([{"pattern": r"\bkubectl\s+delete\b", "action": "deny", "reason": "prod cluster"}], f)
        self.assertEqual(self.verdict("kubectl delete pod x", env={"FLOWKIT_GUARD_RULES": path}), "deny")

    def test_deny_reason_goes_to_stderr(self):
        p = run(GUARD, {"tool_name": "Bash", "tool_input": {"command": "rm -rf ~"}})
        self.assertIn("recursive rm of ~", p.stderr)


if __name__ == "__main__":
    unittest.main()
