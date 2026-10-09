"""Исполнение стартовых команд с отображением диалога."""

from .parser import parse_command


def run_startup(path, shell, emit=print):
    """Выполнить UTF-8 скрипт; ошибки показать с номером строки."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        emit(f"Ошибка чтения скрипта {path}: {error}")
        return False
    for number, line in enumerate(lines, start=1):
        try:
            if not parse_command(line):
                continue
        except ValueError:
            pass
        emit(shell.prompt + line)
        result = shell.execute(line)
        if result.output:
            emit(result.output)
        if result.error:
            emit(f"Ошибка скрипта {path}, строка {number}")
        if result.stop:
            return True
    return False
