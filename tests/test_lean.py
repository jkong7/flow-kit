import json
import os
import subprocess
import tempfile
import unittest

from helpers import BIN, run

LEAN = os.path.join(BIN, "lean")


def git(*args):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t"] + list(args), check=True,
                   capture_output=True)


def write(path, size):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(os.urandom(size))


class LeanTest(unittest.TestCase):
    def setUp(self):
        self.home = os.path.realpath(tempfile.mkdtemp())
        self.dev = os.path.join(self.home, "dev")
        os.makedirs(self.dev)

    def scan(self, *extra):
        p = run(LEAN, args=["--json", "--no-system", "--dev", self.dev] + list(extra), env={"HOME": self.home})
        self.assertEqual(p.returncode, 0, p.stderr)
        return {r["id"]: r for r in json.loads(p.stdout)}

    def repo(self, name):
        path = os.path.join(self.dev, name)
        git("init", "-q", "-b", "main", path)
        git("-C", path, "commit", "-q", "--allow-empty", "-m", "init")
        return path

    def test_empty_machine_reports_nothing(self):
        self.assertEqual(self.scan(), {})

    def test_large_cache_is_safe_and_recommended(self):
        write(os.path.join(self.home, ".npm", "blob"), 101 * 1024 ** 2)
        r = self.scan()["cache:npm"]
        self.assertTrue(r["recommend"])
        self.assertEqual(r["risk"], "safe")
        self.assertEqual(r["action"], "npm cache clean --force")

    def test_small_cache_is_ignored(self):
        write(os.path.join(self.home, ".npm", "blob"), 1024)
        self.assertNotIn("cache:npm", self.scan())

    def test_merged_worktree_is_safe_unmerged_is_review(self):
        repo = self.repo("app")
        merged = os.path.join(self.dev, "wt-merged")
        ahead = os.path.join(self.dev, "wt-ahead")
        git("-C", repo, "worktree", "add", "-q", "-b", "done", merged)
        git("-C", repo, "worktree", "add", "-q", "-b", "wip", ahead)
        git("-C", ahead, "commit", "-q", "--allow-empty", "-m", "local only")
        found = self.scan()
        self.assertTrue(found["worktree:%s" % merged]["recommend"])
        self.assertEqual(found["worktree:%s" % ahead]["risk"], "review")
        self.assertFalse(found["worktree:%s" % ahead]["recommend"])
        self.assertNotIn("--force", found["worktree:%s" % ahead]["action"])

    def test_dirty_worktree_is_review(self):
        repo = self.repo("app")
        wt = os.path.join(self.dev, "wt")
        git("-C", repo, "worktree", "add", "-q", "-b", "x", wt)
        with open(os.path.join(wt, "new.txt"), "w") as f:
            f.write("x")
        r = self.scan()["worktree:%s" % wt]
        self.assertFalse(r["recommend"])
        self.assertIn("uncommitted", r["reason"])

    def test_node_modules_recommended_only_when_idle(self):
        repo = self.repo("web")
        nm = os.path.join(repo, "node_modules")
        write(os.path.join(nm, "pkg"), 51 * 1024 ** 2)
        self.assertFalse(self.scan()["node_modules:%s" % nm]["recommend"])
        old = 1_000_000_000
        for p in (os.path.join(repo, ".git", "logs", "HEAD"), os.path.join(repo, ".git", "index"), repo):
            os.utime(p, (old, old))
        self.assertTrue(self.scan()["node_modules:%s" % nm]["recommend"])

    def test_keep_hides_a_finding(self):
        write(os.path.join(self.home, ".npm", "blob"), 101 * 1024 ** 2)
        p = run(LEAN, args=["--keep", "cache:npm"], env={"HOME": self.home})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn("cache:npm", self.scan())

    def test_text_report_marks_recommended(self):
        write(os.path.join(self.home, ".npm", "blob"), 101 * 1024 ** 2)
        p = run(LEAN, args=["--no-system", "--dev", self.dev], env={"HOME": self.home})
        self.assertIn("== caches ==", p.stdout)
        self.assertIn("* recommended", p.stdout)


if __name__ == "__main__":
    unittest.main()
