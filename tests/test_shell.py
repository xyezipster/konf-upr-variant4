"""Проверки прототипа оболочки."""

import unittest

from src.shell import Shell


class ShellTests(unittest.TestCase):
    """REPL и обработка ошибочных команд."""

    def test_prompt(self):
        self.assertEqual(Shell("Demo").prompt, "Demo:/$ ")

    def test_exit(self):
        self.assertTrue(Shell().execute("exit").stop)
        self.assertTrue(Shell().execute("exit now").error)

    def test_errors(self):
        for line in ["unknown", "cd a b", 'ls "bad']:
            with self.subTest(line=line):
                self.assertTrue(Shell().execute(line).error)

    def test_stubs(self):
        self.assertEqual(Shell().execute("ls /a").output, "ls /a")
        self.assertEqual(Shell().execute("cd /a").output, "cd /a")
