"""Разбор числовых и символьных режимов chmod."""

import re

from .vfs import MODE, parse_mode

SYMBOLIC = re.compile(r"([ugoa]*)([+=-])([rwx]*)")
SHIFTS = {"u": 6, "g": 3, "o": 0}
RIGHTS = {"r": 4, "w": 2, "x": 1}
CLASS_MASK = 0o7


def parse_changes(value):
    """Проверить режим до изменения узлов, вернуть число или действия."""
    if MODE.fullmatch(value):
        return parse_mode(value)
    changes = []
    for clause in value.split(","):
        match = SYMBOLIC.fullmatch(clause)
        if match is None:
            raise ValueError("chmod: неверный режим прав")
        groups, operation, rights = match.groups()
        if not rights and operation != "=":
            raise ValueError("chmod: после + или - нужны права rwx")
        groups = "ugo" if not groups or "a" in groups else groups
        bits = sum(RIGHTS[right] for right in set(rights))
        changes.append((set(groups), operation, bits))
    return changes


def apply_changes(mode, changes):
    """Применить проверенный режим к исходным битам прав."""
    if isinstance(changes, int):
        return changes
    for groups, operation, bits in changes:
        for group in groups:
            shifted = bits << SHIFTS[group]
            if operation == "+":
                mode |= shifted
            elif operation == "-":
                mode &= ~shifted
            else:
                mode = (mode & ~(CLASS_MASK << SHIFTS[group])) | shifted
    return mode
