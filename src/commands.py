"""Команды ls, cd, whoami, cal и du для виртуальной файловой системы."""

import calendar
import getpass
import posixpath
from datetime import date

MAX_CD_ARGUMENTS = 1
MAX_CAL_ARGUMENTS = 2
MIN_MONTH, MAX_MONTH = 1, 12
MIN_YEAR, MAX_YEAR = 1, 9999


def options(arguments, allowed):
    """Разобрать короткие флаги и пути; -- завершает список опций."""
    flags, paths, ended = set(), [], False
    for word in arguments:
        if word == "--" and not ended:
            ended = True
        elif word.startswith("-") and not ended:
            requested = set(word[1:])
            if not requested or not requested <= set(allowed):
                raise ValueError(f"Неподдерживаемая опция: {word}")
            flags.update(requested)
        else:
            paths.append(word)
    return flags, paths


def permissions(node):
    """Показать права в виде rwxr-xr-x с обозначением типа узла."""
    bits = "".join(letter if node.mode & (1 << shift) else "-"
                   for shift, letter in zip(range(8, -1, -1), "rwx" * 3))
    return ("d" if node.kind == "dir" else "-") + bits


def _ls_entry(vfs, path, detailed):
    """Показать имя узла, а с -l ещё права и число байт файла."""
    node = vfs.nodes[path]
    name = posixpath.basename(path) or "/"
    if detailed:
        return f"{permissions(node)} {len(node.data):>6} {name}"
    return name


def _ls_path(shell, path, flags):
    """Сформировать список одного каталога или вывести один файл."""
    vfs = shell.vfs
    if vfs.nodes[path].kind == "file":
        return _ls_entry(vfs, path, "l" in flags)
    children = vfs.children(path)
    if "a" not in flags:
        children = [p for p in children
                    if not posixpath.basename(p).startswith(".")]
    return "\n".join(_ls_entry(vfs, p, "l" in flags) for p in children)


def ls(shell, arguments):
    """ls [-al] [пути...]: вывести содержимое VFS."""
    flags, paths = options(arguments, "al")
    paths = paths or ["."]
    output = []
    for value in paths:
        path = shell.vfs.resolve(value, shell.cwd)
        listing = _ls_path(shell, path, flags)
        if len(paths) > MAX_CD_ARGUMENTS:
            listing = f"{value}:\n{listing}"
        output.append(listing)
    return "\n\n".join(output)


def cd(shell, arguments):
    """cd [путь]: сменить каталог; без аргумента перейти в корень."""
    if len(arguments) > MAX_CD_ARGUMENTS:
        raise ValueError("cd: ожидается не более одного пути")
    path = shell.vfs.resolve(arguments[0] if arguments else "/", shell.cwd)
    if shell.vfs.nodes[path].kind != "dir":
        raise ValueError(f"cd: это не каталог: {path}")
    shell.cwd = path
    return ""


def whoami(shell, arguments):
    """whoami: вернуть имя пользователя реальной ОС."""
    if arguments:
        raise ValueError("whoami: аргументы не поддерживаются")
    return getpass.getuser()


def cal(shell, arguments):
    """cal [год] или cal [месяц год]: показать календарь."""
    if len(arguments) > MAX_CAL_ARGUMENTS:
        raise ValueError("cal: ожидаются год или месяц и год")
    today = date.today()
    try:
        values = [int(value) for value in arguments]
    except ValueError as error:
        raise ValueError("cal: аргументы должны быть целыми числами") from error
    if len(values) == MAX_CAL_ARGUMENTS:
        month, year = values
    elif values:
        month, year = None, values[0]
    else:
        month, year = today.month, today.year
    if not MIN_YEAR <= year <= MAX_YEAR:
        raise ValueError("cal: год должен быть от 1 до 9999")
    if month is not None and not MIN_MONTH <= month <= MAX_MONTH:
        raise ValueError("cal: месяц должен быть от 1 до 12")
    formatter = calendar.TextCalendar(firstweekday=calendar.MONDAY)
    return (formatter.formatmonth(year, month) if month is not None
            else formatter.formatyear(year)).rstrip()


def _size(vfs, path):
    """Суммировать длины файлов без округления до физических блоков."""
    prefix = path.rstrip("/") + "/"
    return sum(len(node.data) for key, node in vfs.nodes.items()
               if key == path or key.startswith(prefix))


def du(shell, arguments):
    """du [-s] [пути...]: показать логический размер VFS в байтах."""
    flags, paths = options(arguments, "s")
    lines = []
    for value in paths or ["."]:
        path = shell.vfs.resolve(value, shell.cwd)
        prefix = path.rstrip("/") + "/"
        directories = [] if "s" in flags else sorted(
            key for key, node in shell.vfs.nodes.items()
            if key.startswith(prefix) and node.kind == "dir" and key != path)
        for key in [*directories, path]:
            lines.append(f"{_size(shell.vfs, key)}\t{key}")
    return "\n".join(lines)


COMMANDS = {"ls": ls, "cd": cd, "whoami": whoami, "cal": cal, "du": du}
