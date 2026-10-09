"""Настройки, журнал и стартовые команды."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.config import parse_config
from src.eventlog import EventLog
from src.shell import Shell
from src.startup import run_startup


class ConfigTests(unittest.TestCase):
    """Пути, приглашение и все параметры запуска."""

    def test_parameters(self):
        config = parse_config(["--vfs", "a.json", "--log", "log.json",
                               "--startup", "start.txt"])
        self.assertEqual(config.name, "a")
        self.assertEqual(config.startup, Path("start.txt"))
        self.assertIn("log.json", config.debug())

    def test_defaults(self):
        self.assertEqual(parse_config([]).name, "MyVFS")

    def test_log_cannot_overwrite_input(self):
        with patch("sys.stderr"), self.assertRaises(SystemExit):
            parse_config(["--vfs", "a.json", "--log", "./a.json"])

    def test_log_cannot_overwrite_hardlinked_vfs(self):
        with tempfile.TemporaryDirectory() as folder:
            source, log = Path(folder)/"vfs.json", Path(folder)/"log.json"
            source.write_text('{"entries": []}')
            log.hardlink_to(source)
            with patch("sys.stderr"), self.assertRaises(SystemExit):
                parse_config(["--vfs", str(source), "--log", str(log)])
            self.assertEqual(source.read_text(), '{"entries": []}')


class StartupTests(unittest.TestCase):
    """Ошибки, комментарии, exit и сохранение событий."""

    def test_script_and_log(self):
        with tempfile.TemporaryDirectory() as folder:
            script, log = Path(folder)/"s.txt", Path(folder)/"log.json"
            script.write_text('# comment\nls\nunknown\nexit\nls\n')
            output = []
            shell = Shell(logger=EventLog(log))
            self.assertTrue(run_startup(script, shell, output.append))
            events = json.loads(log.read_text())
            self.assertEqual(len(events), 3)
            self.assertEqual(events[1]["status"], "error")
            self.assertTrue(events[0]["user"])
            self.assertTrue(any("строка 3" in line for line in output))
            self.assertEqual(len(EventLog(log).events), 3)

    def test_missing_script(self):
        output = []
        self.assertFalse(run_startup(Path("absent"), Shell(),
                                     output.append))
        self.assertIn("Ошибка чтения", output[0])

    def test_invalid_log(self):
        with tempfile.TemporaryDirectory() as folder:
            log = Path(folder)/"log.json"
            log.write_text('{}')
            with self.assertRaises(ValueError):
                EventLog(log)
