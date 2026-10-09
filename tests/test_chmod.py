"""Изменение прав и сохранность физического JSON."""

import tempfile
import unittest
from pathlib import Path

from src.shell import Shell
from src.vfs import VFS

DATA = Path(__file__).resolve().parents[1] / "data"


class ChmodTests(unittest.TestCase):
    """Числовой, символьный и рекурсивный режимы chmod."""

    def setUp(self):
        self.shell = Shell(vfs=VFS.load(DATA / "demo.json"))

    def test_numeric(self):
        result = self.shell.execute("chmod 600 /hello.txt")
        self.assertFalse(result.error)
        self.assertIn("-rw-------", self.shell.execute("ls -l").output)

    def test_symbolic(self):
        self.shell.execute("chmod u+x,g-r,o= /hello.txt")
        self.assertEqual(self.shell.vfs.nodes["/hello.txt"].mode, 0o700)
        self.shell.execute("chmod a=rx /hello.txt")
        self.assertEqual(self.shell.vfs.nodes["/hello.txt"].mode, 0o555)
        self.shell.execute("chmod +w /hello.txt")
        self.assertEqual(self.shell.vfs.nodes["/hello.txt"].mode, 0o777)

    def test_symbolic_mode_starting_with_minus(self):
        self.shell.execute("chmod -w /hello.txt")
        self.assertEqual(self.shell.vfs.nodes["/hello.txt"].mode, 0o444)
        self.shell.execute("chmod -R -r /docs")
        self.assertEqual(self.shell.vfs.nodes["/docs/readme.txt"].mode,
                         0o200)

    def test_recursive_and_multiple(self):
        self.shell.execute("chmod -R 700 /home")
        modes = [node.mode for path, node in self.shell.vfs.nodes.items()
                 if path.startswith("/home")]
        self.assertEqual(set(modes), {0o700})
        self.shell.execute("chmod 600 /hello.txt /docs/readme.txt")
        self.assertEqual(self.shell.vfs.nodes["/docs/readme.txt"].mode,
                         0o600)

    def test_invalid_changes_are_atomic(self):
        for line in ["chmod 999 /hello.txt", "chmod u+z /hello.txt",
                     "chmod u+x,bad /hello.txt", "chmod 600",
                     "chmod 600 /hello.txt /missing", "chmod u+ /hello.txt"]:
            with self.subTest(line=line):
                self.assertTrue(self.shell.execute(line).error)
                self.assertEqual(self.shell.vfs.nodes["/hello.txt"].mode,
                                 0o644)

    def test_source_unchanged_and_reload(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.json"
            source = (DATA / "demo.json").read_bytes()
            path.write_bytes(source)
            shell = Shell(vfs=VFS.load(path))
            shell.execute("chmod -R 000 /")
            self.assertEqual(path.read_bytes(), source)
            self.assertEqual(VFS.load(path).nodes["/hello.txt"].mode, 0o644)
