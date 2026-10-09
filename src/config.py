"""Параметры запуска и отладочный вывод."""

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Физические пути VFS, журнала и стартового скрипта."""

    vfs: Path | None = None
    log: Path | None = None
    startup: Path | None = None

    @property
    def name(self):
        """Имя VFS в приглашении берётся из имени файла."""
        return self.vfs.stem if self.vfs else "MyVFS"

    def debug(self):
        """Показать все настройки перед началом диалога."""
        return (f"VFS: {self.vfs or '(в памяти)'}\n"
                f"Лог: {self.log or '(отключён)'}\n"
                f"Стартовый скрипт: {self.startup or '(не задан)'}")



def _same_file(first, second):
    """Сравнить пути, включая символические и жёсткие ссылки."""
    if first.resolve() == second.resolve():
        return True
    return first.exists() and second.exists() and first.samefile(second)

def parse_config(arguments=None):
    """Прочитать необязательные пути из командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор, вариант 4")
    parser.add_argument("--vfs", type=Path, help="JSON-файл VFS")
    parser.add_argument("--log", type=Path, help="JSON-журнал команд")
    parser.add_argument("--startup", type=Path, help="Скрипт UTF-8")
    values = parser.parse_args(arguments)
    paths = (values.vfs, values.log, values.startup)
    if values.log and any(_same_file(values.log, path)
                          for path in (values.vfs, values.startup) if path):
        parser.error("Лог не должен совпадать с VFS или скриптом")
    return Config(*paths)
