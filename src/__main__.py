"""Точка входа консольного приложения."""

import sys

from .config import parse_config
from .eventlog import EventLog
from .shell import Shell
from .startup import run_startup
from .vfs import VFS


def repl(shell):
    """Читать команды до exit или конца стандартного ввода."""
    while True:
        try:
            line = input(shell.prompt)
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            continue
        result = shell.execute(line)
        if result.output:
            print(result.output)
        if result.stop:
            break


def main(arguments=None):
    """Настроить журнал, выполнить скрипт и открыть REPL."""
    config = parse_config(arguments)
    print(config.debug())
    try:
        vfs = VFS.load(config.vfs) if config.vfs else VFS()
        shell = Shell(config.name, EventLog(config.log), vfs)
        if config.startup and run_startup(config.startup, shell):
            return 0
        repl(shell)
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Ошибка запуска или записи лога: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
