import os
import stat
import tempfile
import unittest

from helpers import BIN, run

ASK = os.path.join(BIN, "ask")


class AskTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.log = os.path.join(self.dir, "claude.log")
        self.claude = os.path.join(self.dir, "claude")
        with open(self.claude, "w") as f:
            f.write(
                "#!/usr/bin/env python3\n"
                "import sys, os, json\n"
                "stdin = sys.stdin.read()\n"
                "open(%r, 'w').write(json.dumps({'argv': sys.argv[1:], 'stdin': stdin,"
                " 'nested': 'CLAUDECODE' in os.environ or 'CLAUDE_CODE_SESSION_ID' in os.environ}))\n"
                "print('RESULT:' + stdin.strip().upper())\n" % self.log)
        os.chmod(self.claude, os.stat(self.claude).st_mode | stat.S_IEXEC)
        self.clip = os.path.join(self.dir, "clip")
        for name, body in (("pbcopy", "cat > %s" % self.clip), ("pbpaste", "cat %s 2>/dev/null" % self.clip)):
            p = os.path.join(self.dir, name)
            with open(p, "w") as f:
                f.write("#!/bin/sh\n%s\n" % body)
            os.chmod(p, 0o755)
        self.env = {"FLOWKIT_CLAUDE_BIN": self.claude, "PATH": self.dir + ":/usr/bin:/bin",
                    "CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "abc"}

    def ask(self, *args, stdin=None, **env):
        e = dict(self.env)
        e.update(env)
        if stdin is None:
            e.setdefault("FLOWKIT_IGNORE_STDIN", "1")
        return run(ASK, args=args, env=e, stdin=stdin)

    def call(self):
        import json
        with open(self.log) as f:
            return json.load(f)

    def clipboard(self):
        with open(self.clip) as f:
            return f.read()

    def test_arg_input_goes_to_claude_and_clipboard(self):
        p = self.ask("fix", "teh cat")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout.strip(), "RESULT:TEH CAT")
        self.assertEqual(self.clipboard(), "RESULT:TEH CAT")
        c = self.call()
        self.assertEqual(c["stdin"], "teh cat")
        self.assertIn("--system-prompt", c["argv"])
        self.assertIn("Fix spelling", c["argv"][c["argv"].index("--system-prompt") + 1])
        self.assertEqual(c["argv"][c["argv"].index("--model") + 1], "haiku")
        self.assertEqual(c["argv"][c["argv"].index("--tools") + 1], "")

    def test_nested_claude_env_is_scrubbed(self):
        self.ask("fix", "x")
        self.assertFalse(self.call()["nested"])

    def test_stdin_input(self):
        p = self.ask("tldr", stdin="long text here")
        self.assertEqual(p.stdout.strip(), "RESULT:LONG TEXT HERE")

    def test_clipboard_fallback(self):
        with open(self.clip, "w") as f:
            f.write("from clipboard")
        self.ask("explain")
        self.assertEqual(self.call()["stdin"], "from clipboard")

    def test_reply_uses_clipboard_as_message_and_arg_as_intent(self):
        with open(self.clip, "w") as f:
            f.write("Can you meet Tuesday?")
        self.ask("reply", "yes but 3pm")
        self.assertEqual(self.call()["stdin"], "Can you meet Tuesday?\n\nINTENT: yes but 3pm")

    def test_unknown_preset_is_a_question(self):
        self.ask("what", "is", "a", "monad")
        c = self.call()
        self.assertEqual(c["stdin"], "what is a monad")
        self.assertIn("Answer concisely", c["argv"][c["argv"].index("--system-prompt") + 1])

    def test_custom_preset_file(self):
        cfg = os.path.join(self.dir, "cfg")
        os.makedirs(os.path.join(cfg, "prompts"))
        with open(os.path.join(cfg, "prompts", "pirate.md"), "w") as f:
            f.write("Talk like a pirate.")
        self.ask("pirate", "hello", FLOWKIT_CONFIG_DIR=cfg)
        c = self.call()
        self.assertEqual(c["argv"][c["argv"].index("--system-prompt") + 1], "Talk like a pirate.")
        p = self.ask("--list", FLOWKIT_CONFIG_DIR=cfg)
        self.assertIn("pirate", p.stdout)
        self.assertIn("commit", p.stdout)

    def test_model_override_and_no_copy(self):
        self.ask("fix", "a", "-m", "sonnet", "--no-copy")
        self.assertEqual(self.call()["argv"][2], "sonnet")
        self.assertFalse(os.path.exists(self.clip))

    def test_commit_reads_staged_diff(self):
        import subprocess
        repo = tempfile.mkdtemp()
        subprocess.run(["git", "-C", repo, "init", "-q"], check=True)
        with open(os.path.join(repo, "a.txt"), "w") as f:
            f.write("hello\n")
        subprocess.run(["git", "-C", repo, "add", "a.txt"], check=True)
        e = dict(self.env, FLOWKIT_IGNORE_STDIN="1")
        import sys
        p = subprocess.run([sys.executable, ASK, "commit"], cwd=repo, env=dict(e, HOME=repo),
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("+hello", self.call()["stdin"])

    def test_no_input_errors(self):
        p = self.ask("fix")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("no input", p.stderr)

    def test_claude_failure_surfaces(self):
        with open(self.claude, "w") as f:
            f.write("#!/bin/sh\necho 'not logged in' >&2\nexit 1\n")
        p = self.ask("fix", "x")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("not logged in", p.stderr)


if __name__ == "__main__":
    unittest.main()
