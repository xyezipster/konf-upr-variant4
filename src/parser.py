"""Разбор команд с кавычками и переменными окружения."""

from dataclasses import dataclass, field
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


@dataclass
class TokenState:
    """Текущий токен и контекст кавычек при чтении строки."""

    tokens: list = field(default_factory=list)
    token: list = field(default_factory=list)
    quote: str | None = None
    started: bool = False

    def append(self, value):
        """Добавить часть слова, включая пустое значение переменной."""
        self.token.append(value)
        self.started = True

    def flush(self):
        """Завершить слово, если оно началось."""
        if self.started:
            self.tokens.append("".join(self.token))
        self.token, self.started = [], False


def _special(line, index, environ, state):
    """Обработать экранирование, кавычки и раскрытие переменной."""
    char = line[index]
    if char == "\\" and state.quote != "'":
        index += 1
        if index == len(line):
            raise ValueError("Незавершённое экранирование")
        state.append(line[index])
        return index + 1
    if char in "\"'" and (state.quote is None or state.quote == char):
        state.quote = None if state.quote else char
        state.started = True
        return index + 1
    if char == "$" and state.quote != "'":
        value, end = _expand(line, index, environ)
        state.append(value)
        return end
    return None


def _step(line, index, environ, state):
    """Прочитать символ или остановиться на комментарии."""
    end = _special(line, index, environ, state)
    if end is not None:
        return end
    char = line[index]
    if char == "#" and state.quote is None and not state.started:
        return len(line)
    if char.isspace() and state.quote is None:
        state.flush()
    else:
        state.append(char)
    return index + 1


def _tokens(line, environ):
    """Разбить строку, сохранив смысл кавычек и экранирования."""
    state = TokenState()
    index = 0
    while index < len(line):
        index = _step(line, index, environ, state)
    if state.quote:
        raise ValueError("Незакрытая кавычка")
    state.flush()
    return state.tokens


def parse_command(line, environ=None):
    """Получить слова команды; одиночные кавычки запрещают раскрытие."""
    return _tokens(line, os.environ if environ is None else environ)
