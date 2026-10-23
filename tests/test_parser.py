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

    def test_adjacent_quoted_parts(self):
        words = parse_command("ls ab\"cd\"'ef' \"\"''")
        self.assertEqual(words, ["ls", "abcdef", ""])

    def test_escaped_characters(self):
        self.assertEqual(parse_command(r"cd my\ dir"), ["cd", "my dir"])
        self.assertEqual(parse_command(r'ls "a\"b"'), ["ls", 'a"b'])
        self.assertEqual(parse_command(r"ls 'a\b'"), ["ls", r"a\b"])

    def test_hash_in_words_and_quotes(self):
        words = parse_command(r'ls \#name "#quoted" a#b # comment')
        self.assertEqual(words, ["ls", "#name", "#quoted", "a#b"])

    def test_variable_boundaries(self):
        environ = {"HOME": "/a b", "NAME_SUFFIX": "value", "EMPTY": ""}
        words = parse_command('ls ${HOME}/docs $NAME_SUFFIX x${EMPTY}y',
                              environ)
        self.assertEqual(words, ["ls", "/a b/docs", "value", "xy"])

    def test_empty_and_comment_lines(self):
        for line in ["", "   ", "\t", " # comment", "\t# comment"]:
            with self.subTest(line=line):
                self.assertEqual(parse_command(line), [])
