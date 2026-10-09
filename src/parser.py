"""Разбор команд с кавычками и переменными окружения."""

import os
import re

VARIABLE = re.compile(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}"
                      r"|([A-Za-z_][A-Za-z0-9_]*))")


def _expand(line, index, environ):
    """Вернуть значение переменной и позицию следующего символа."""
    match = VARIABLE.match(line, index)
    if match is None:
        return "$", index + 1
    name = match.group(1) or match.group(2)
    return environ.get(name, ""), match.end()


def _tokens(line, environ):
    """Разбить строку, сохранив смысл кавычек и экранирования."""
    tokens, token, quote = [], [], None
    index, started = 0, False
    while index < len(line):
        char = line[index]
        if char == "\\" and quote != "'":
            index += 1
            if index == len(line):
                raise ValueError("Незавершённое экранирование")
            token.append(line[index])
            started = True
        elif char in "\"'" and (quote is None or quote == char):
            quote = None if quote else char
            started = True
        elif char == "#" and quote is None and not started:
            break
        elif char.isspace() and quote is None:
            if started:
                tokens.append("".join(token))
            token, started = [], False
        elif char == "$" and quote != "'":
            value, index = _expand(line, index, environ)
            token.append(value)
            started = True
            continue
        else:
            token.append(char)
            started = True
        index += 1
    if quote:
        raise ValueError("Незакрытая кавычка")
    if started:
        tokens.append("".join(token))
    return tokens


def parse_command(line, environ=None):
    """Получить слова команды; одиночные кавычки запрещают раскрытие."""
    return _tokens(line, os.environ if environ is None else environ)
