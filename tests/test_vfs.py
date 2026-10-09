"""Загрузка JSON, двоичные файлы и виртуальные пути."""

import json
import tempfile
import unittest
from pathlib import Path

from src.vfs import VFS

DATA = Path(__file__).resolve().parents[1] / "data"


class VFSTests(unittest.TestCase):
    """Правильные и ошибочные источники файловой системы."""

    def test_default(self):
        self.assertEqual(VFS().children("/"), [])

    def test_binary_and_utf8(self):
        vfs = VFS.load(DATA / "files.json")
        self.assertEqual(vfs.nodes["/binary.bin"].data,
                         bytes([0, 1, 255, 128]))
        self.assertEqual(vfs.nodes["/hello.txt"].data.decode(), "Привет!\n")

    def test_deep_paths(self):
        vfs = VFS.load(DATA / "deep.json")
        path = vfs.resolve("../student/./docs", "/home/student")
        self.assertEqual(path, "/home/student/docs")
        self.assertEqual(vfs.resolve("../../../../", path), "/")

    def test_missing_and_invalid(self):
        for name in ["missing.json", "invalid.json"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                VFS.load(DATA / name)

    def test_invalid_documents(self):
        cases = [[], {}, {"entries": []}, {"entries": [None]},
                 {"entries": [{"path": "/", "type": "file",
                               "encoding": "base64", "data": "!"}]}]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.json"
            for document in cases:
                path.write_text(json.dumps(document))
                with self.subTest(document=document):
                    with self.assertRaises(ValueError):
                        VFS.load(path)

    def test_tree_validation(self):
        root = {"path": "/", "type": "dir"}
        cases = [root, {"path": "/missing/child", "type": "dir"},
                 {"path": "/../x", "type": "dir"},
                 {"path": "/x", "type": "dir", "mode": "999"}]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.json"
            for entry in cases:
                path.write_text(json.dumps({"entries": [root, entry]}))
                with self.subTest(entry=entry), self.assertRaises(ValueError):
                    VFS.load(path)
