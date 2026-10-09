"""Виртуальная файловая система; данные существуют только в памяти."""

import base64
import binascii
import json
import posixpath
import re
from dataclasses import dataclass

MODE = re.compile(r"[0-7]{3}")


@dataclass
class Node:
    """Каталог или файл с содержимым в байтах и правами доступа."""

    kind: str
    mode: int
    data: bytes = b""


def parse_mode(value):
    """Разобрать три восьмеричные цифры прав доступа."""
    if not isinstance(value, str) or MODE.fullmatch(value) is None:
        raise ValueError("Права должны содержать три цифры от 0 до 7")
    return int(value, 8)


def _decode_node(entry):
    """Проверить тип узла и декодировать base64 для файла."""
    if not isinstance(entry, dict):
        raise ValueError("Элемент VFS должен быть объектом")
    kind = entry.get("type")
    if kind not in ("file", "dir"):
        raise ValueError("Тип узла должен быть file или dir")
    mode = parse_mode(entry.get("mode", "755" if kind == "dir" else "644"))
    if kind == "dir":
        if "data" in entry:
            raise ValueError("Каталог не должен содержать data")
        return Node(kind, mode)
    if entry.get("encoding") != "base64":
        raise ValueError("Для файла требуется encoding: base64")
    try:
        data = base64.b64decode(entry["data"], validate=True)
    except (KeyError, TypeError, ValueError, binascii.Error) as error:
        raise ValueError("Неверные данные base64") from error
    return Node(kind, mode, data)


def _entry_path(entry):
    """Проверить абсолютный канонический путь узла."""
    path = entry.get("path")
    if not isinstance(path, str) or not path.startswith("/"):
        raise ValueError("Путь узла должен быть абсолютным")
    if "\x00" in path or path.startswith("//"):
        raise ValueError("Недопустимый путь VFS")
    if posixpath.normpath(path) != path:
        raise ValueError("Пути VFS должны быть без .. и завершающего /")
    return path


class VFS:
    """Загружать JSON и работать с узлами без записи исходного файла."""

    def __init__(self, nodes=None):
        """Без источника создать корневой каталог в памяти."""
        self.nodes = nodes if nodes is not None else {"/": Node("dir", 0o755)}

    @classmethod
    def load(cls, path):
        """Прочитать и проверить JSON-файл без распаковки на диск."""
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(document, dict):
                raise ValueError("Корень JSON должен быть объектом")
            entries = document.get("entries")
            if not isinstance(entries, list):
                raise ValueError("Поле entries должно быть списком")
            nodes = {}
            for entry in entries:
                node = _decode_node(entry)
                key = _entry_path(entry)
                if key in nodes:
                    raise ValueError(f"Повторяющийся путь: {key}")
                nodes[key] = node
            vfs = cls(nodes)
            vfs._validate_tree()
            return vfs
        except (OSError, ValueError, UnicodeError) as error:
            raise ValueError(f"Ошибка загрузки VFS {path}: {error}") from error

    def _validate_tree(self):
        """Убедиться в наличии корня и родительских каталогов."""
        if "/" not in self.nodes or self.nodes["/"].kind != "dir":
            raise ValueError("VFS должна содержать корневой каталог /")
        for path in self.nodes:
            parent = posixpath.dirname(path)
            if parent not in self.nodes or self.nodes[parent].kind != "dir":
                raise ValueError(f"Нет родительского каталога: {path}")

    def resolve(self, path, cwd="/"):
        """Нормализовать виртуальный путь с учётом . и .. ."""
        if not path or "\x00" in path:
            raise ValueError("Путь не должен быть пустым или содержать NUL")
        joined = posixpath.join(cwd, path)
        resolved = "/" + posixpath.normpath(joined).lstrip("/")
        if resolved not in self.nodes:
            raise ValueError(f"Путь не найден: {path}")
        return resolved

    def children(self, path):
        """Вернуть отсортированные пути непосредственных потомков."""
        if self.nodes[path].kind != "dir":
            raise ValueError(f"Это не каталог: {path}")
        return sorted(key for key in self.nodes if key != path
                      and posixpath.dirname(key) == path)
