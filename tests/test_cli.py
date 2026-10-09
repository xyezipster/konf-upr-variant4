"""Проверки приложения как отдельного процесса."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(arguments, input_text="exit\n"):
    """Запустить приложение без зависимости от shell-скрипта."""
    return subprocess.run([sys.executable, "-B", "-m", "src", *arguments],
                          cwd=ROOT, input=input_text, text=True,
                          capture_output=True, timeout=10)


class CLITests(unittest.TestCase):
    """Коды завершения, ошибки запуска и полный сценарий."""

    def test_default_and_help(self):
        result = run_cli([])
        self.assertEqual(result.returncode, 0)
        self.assertIn("MyVFS:/$", result.stdout)
        self.assertIn("--startup", run_cli(["--help"]).stdout)

    def test_missing_vfs(self):
        result = run_cli(["--vfs", "data/missing.json"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Ошибка загрузки VFS", result.stderr)

    def test_complete_script_and_source(self):
        with tempfile.TemporaryDirectory() as folder:
            script, log = Path(folder)/"s.txt", Path(folder)/"log.json"
            script.write_text('whoami\nchmod 600 /hello.txt\n'
                              'ls -l /hello.txt\nexit\n', encoding="utf-8")
            source = (ROOT/"data/demo.json").read_bytes()
            result = run_cli(["--vfs", "data/demo.json", "--log", str(log),
                              "--startup", str(script)])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("-rw-------", result.stdout)
            self.assertEqual(len(json.loads(log.read_text())), 4)
            self.assertEqual((ROOT/"data/demo.json").read_bytes(), source)

    def test_missing_script_keeps_repl(self):
        result = run_cli(["--startup", "missing.txt"])
        self.assertIn("Ошибка чтения скрипта", result.stdout)
        self.assertIn("MyVFS:/$", result.stdout)
