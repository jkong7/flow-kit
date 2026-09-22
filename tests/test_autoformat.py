import os
import stat
import tempfile
import unittest

from helpers import HOOKS, run

FORMAT = os.path.join(HOOKS, "autoformat.py")

class AutoformatTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.bin = os.path.join(self.dir, "node_modules", ".bin")
        os.makedirs(self.bin)

    def fake(self, name):
        path = os.path.join(self.bin, name)
        with open(path, "w") as f:
            f.write("#!/bin/sh\necho \"$0 $@\" >> %s/calls.log\n" % self.dir)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    def touch(self, name):
        path = os.path.join(self.dir, name)
        open(path, "w").close()
        return path

    def test_project_local_prettier_is_run(self):
        self.fake("prettier")
        path = self.touch("app.tsx")
        p = run(FORMAT, {"tool_name": "Write", "tool_input": {"file_path": path}}, env={"PATH": "/usr/bin:/bin"})
        self.assertEqual(p.returncode, 0)
        with open(os.path.join(self.dir, "calls.log")) as f:
            self.assertIn("--write", f.read())

    def test_dry_run_and_relative_path(self):
        self.fake("prettier")
        self.touch("data.json")
        p = run(FORMAT, {"tool_name": "Edit", "cwd": self.dir, "tool_input": {"file_path": "data.json"}},
                env={"PATH": "/usr/bin:/bin", "FLOWKIT_DRY_RUN": "1"})
        self.assertIn("prettier", p.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "calls.log")))

    def test_no_formatter_is_a_noop(self):
        path = self.touch("main.go")
        p = run(FORMAT, {"tool_input": {"file_path": path}}, env={"PATH": "/nonexistent", "FLOWKIT_DRY_RUN": "1"})
        self.assertEqual((p.returncode, p.stdout), (0, ""))

    def test_missing_file_and_off_switch(self):
        self.fake("prettier")
        p = run(FORMAT, {"tool_input": {"file_path": "/nope/x.ts"}}, env={"FLOWKIT_DRY_RUN": "1"})
        self.assertEqual(p.stdout, "")
        path = self.touch("a.ts")
        p = run(FORMAT, {"tool_input": {"file_path": path}}, env={"FLOWKIT_DRY_RUN": "1", "FLOWKIT_FORMAT_OFF": "1"})
        self.assertEqual(p.stdout, "")


if __name__ == "__main__":
    unittest.main()
