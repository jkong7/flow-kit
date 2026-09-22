import os
import tempfile
import unittest

from helpers import BIN, run

CAPTURE = os.path.join(BIN, "capture")


class CaptureTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.inbox = os.path.join(self.dir, "sub", "inbox.md")
        self.env = {"FLOWKIT_INBOX": self.inbox, "FLOWKIT_NOW": "2026-09-21 14:03"}

    def cap(self, *args, stdin=None, **env):
        e = dict(self.env)
        e.update(env)
        return run(CAPTURE, args=args, env=e, stdin=stdin)

    def read(self):
        with open(self.inbox) as f:
            return f.read()

    def test_append_creates_file_with_header(self):
        p = self.cap("email", "prof  about\textension")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.read(), "# Inbox\n\n- [ ] 2026-09-21 14:03 email prof about extension\n")
        self.cap("second")
        self.assertTrue(self.read().endswith("- [ ] 2026-09-21 14:03 second\n"))
        self.assertEqual(self.read().count("# Inbox"), 1)

    def test_stdin(self):
        self.cap(stdin="multi\nline idea\n")
        self.assertIn("- [ ] 2026-09-21 14:03 multi line idea", self.read())

    def test_tab_capture(self):
        self.cap("--tab", "read later", FLOWKIT_FRONT_TAB="https://ex.com/a\nAn [Article]")
        self.assertIn("[An [Article)](https://ex.com/a) read later", self.read())

    def test_list_count_done(self):
        for t in ("one", "two", "three"):
            self.cap(t)
        self.assertEqual(self.cap("--count").stdout.strip(), "3")
        self.assertIn(" 2. 2026-09-21 14:03 two", self.cap("--list").stdout)
        self.assertEqual(self.cap("--done", "2").returncode, 0)
        self.assertIn("- [x] 2026-09-21 14:03 two", self.read())
        self.assertEqual(self.cap("--count").stdout.strip(), "2")
        self.assertIn(" 2. 2026-09-21 14:03 three", self.cap("--list").stdout)
        self.assertNotEqual(self.cap("--done", "9").returncode, 0)

    def test_empty_is_an_error(self):
        p = self.cap(stdin="")
        self.assertNotEqual(p.returncode, 0)

    def test_dry_run_writes_nothing(self):
        p = self.cap("x", FLOWKIT_DRY_RUN="1")
        self.assertIn("DRY", p.stdout)
        self.assertFalse(os.path.exists(self.inbox))

    def test_count_with_no_inbox(self):
        self.assertEqual(self.cap("--count").stdout.strip(), "0")


if __name__ == "__main__":
    unittest.main()
