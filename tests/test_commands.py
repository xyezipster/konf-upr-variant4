"""Проверки основных команд в нескольких режимах."""

import unittest
from pathlib import Path
from unittest.mock import patch

from src.shell import Shell
from src.vfs import VFS

DATA = Path(__file__).resolve().parents[1] / "data"


class CommandTests(unittest.TestCase):
    """Листинг, перемещение, календарь и размер файлов."""

    def setUp(self):
        self.shell = Shell("Demo", vfs=VFS.load(DATA / "demo.json"))

    def test_ls(self):
        output = self.shell.execute("ls").output
        self.assertIn("hello.txt", output)
        self.assertNotIn(".hidden", output)
        output = self.shell.execute("ls -al").output
        self.assertIn("-rw-r--r--", output)
        self.assertIn(".hidden", output)
        self.assertIn("/docs:", self.shell.execute("ls /docs /home").output)
        self.assertEqual(self.shell.execute("ls /hello.txt").output,
                         "hello.txt")

    def test_cd(self):
        self.assertFalse(self.shell.execute("cd /home/student/docs").error)
        self.assertEqual(self.shell.cwd, "/home/student/docs")
        self.assertFalse(self.shell.execute("cd ..").error)
        self.assertEqual(self.shell.cwd, "/home/student")
        self.shell.execute("cd")
        self.assertEqual(self.shell.cwd, "/")
        self.shell.execute("cd /hello.txt")
        self.assertEqual(self.shell.cwd, "/")

    def test_whoami(self):
        with patch("src.commands.getpass.getuser", return_value="student"):
            self.assertEqual(self.shell.execute("whoami").output, "student")

    def test_cal(self):
        output = self.shell.execute("cal 2 2024").output
        self.assertIn("February 2024", output)
        self.assertIn("29", output)
        self.assertIn("December", self.shell.execute("cal 2026").output)
        self.assertFalse(self.shell.execute("cal").error)

    def test_du(self):
        total = sum(len(n.data) for n in self.shell.vfs.nodes.values())
        self.assertEqual(self.shell.execute("du -s /").output,
                         f"{total}\t/")
        self.assertEqual(self.shell.execute("du /hello.txt").output,
                         "7\t/hello.txt")
        self.assertIn("/home/student/docs", self.shell.execute("du").output)
        output = self.shell.execute("du -s /docs /home").output
        self.assertEqual(len(output.splitlines()), 2)

    def test_errors(self):
        cases = ["ls -z", "ls /missing", "ls ''", "cd /hello.txt",
                 "whoami user", "cal 13 2026", "cal 0", "cal text",
                 "cal 1 2 3", "du -x", "du /missing"]
        for line in cases:
            with self.subTest(line=line):
                self.assertTrue(self.shell.execute(line).error)
