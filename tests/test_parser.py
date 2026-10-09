"""Проверки разбора команд."""

import unittest

from src.parser import parse_command


class ParserTests(unittest.TestCase):
    """Кавычки, переменные и ошибки ввода."""

    def test_quotes_and_empty_argument(self):
        self.assertEqual(parse_command('cd "my dir"'), ["cd", "my dir"])
        self.assertEqual(parse_command('ls ""'), ["ls", ""])

    def test_environment(self):
        env = {"HOME": "/a b", "USER": "student"}
        words = parse_command('ls "$HOME" ${USER} $MISSING', env)
        self.assertEqual(words, ["ls", "/a b", "student", ""])

    def test_single_quotes_and_escape(self):
        words = parse_command("ls '$HOME' \\$HOME", {"HOME": "/a"})
        self.assertEqual(words, ["ls", "$HOME", "$HOME"])

    def test_comments(self):
        self.assertEqual(parse_command("# comment"), [])
        self.assertEqual(parse_command("ls # comment"), ["ls"])
        self.assertEqual(parse_command('ls "# x" a#b'),
                         ["ls", "# x", "a#b"])

    def test_errors(self):
        for line in ['ls "oops', "ls " + chr(92)]:
            with self.subTest(line=line), self.assertRaises(ValueError):
                parse_command(line)
