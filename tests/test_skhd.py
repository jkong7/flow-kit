import os
import re
import unittest

from helpers import ROOT

SKHD = os.path.join(ROOT, "skhd", "skhdrc.example")
LINE = re.compile(r"^(hyper|cmd|alt|ctrl|shift)(\s*\+\s*\w+)*\s+-\s+\w+\s+:\s+\S.*$")


class SkhdTest(unittest.TestCase):
    def setUp(self):
        with open(SKHD) as f:
            self.lines = [l.rstrip("\n") for l in f if l.strip()]

    def test_every_line_is_a_binding(self):
        for line in self.lines:
            self.assertRegex(line, LINE)

    def test_no_duplicate_keys(self):
        keys = [l.split(":", 1)[0].strip() for l in self.lines]
        self.assertEqual(len(keys), len(set(keys)))

    def test_targets_exist(self):
        scripts = {f[:-3] for f in os.listdir(os.path.join(ROOT, "raycast")) if f.endswith(".sh")}
        for line in self.lines:
            cmd = line.split(":", 1)[1]
            for slug in re.findall(r"raycast://script-commands/([\w-]+)", cmd):
                self.assertIn(slug, scripts, line)
            for tool in re.findall(r"flow-kit/bin/(\w+)", cmd):
                self.assertTrue(os.access(os.path.join(ROOT, "bin", tool), os.X_OK), line)

    def test_does_not_steal_existing_cmd_number_shortcuts(self):
        for line in self.lines:
            self.assertFalse(re.match(r"^cmd\s+-\s+[0-9]\b", line), line)


if __name__ == "__main__":
    unittest.main()
