"""Выполнение команд и состояние эмулятора."""

from dataclasses import dataclass

from .parser import parse_command

MAX_CD_ARGUMENTS = 1


@dataclass
class Result:
    """Текст результата, признак ошибки и запрос завершения."""

    output: str = ""
    error: bool = False
    stop: bool = False


class Shell:
    """Обрабатывать одну строку команды за вызов."""

    def __init__(self, name="MyVFS"):
        """Задать имя VFS для приглашения."""
        self.name = name
        self.cwd = "/"

    @property
    def prompt(self):
        """Приглашение содержит имя VFS и текущий каталог."""
        return f"{self.name}:{self.cwd}$ "

    def execute(self, line):
        """Вернуть результат без исполнения команд реальной ОС."""
        try:
            words = parse_command(line)
            if not words:
                return Result()
            return self.dispatch(words[0], words[1:])
        except ValueError as error:
            return Result(str(error), error=True)

    def dispatch(self, command, arguments):
        """Обработать exit и команды-заглушки этапа 1."""
        if command == "exit":
            if arguments:
                raise ValueError("exit: аргументы не поддерживаются")
            return Result(stop=True)
        if command == "cd" and len(arguments) > MAX_CD_ARGUMENTS:
            raise ValueError("cd: ожидается не более одного пути")
        if command in {"ls", "cd"}:
            return Result(" ".join([command, *arguments]))
        raise ValueError(f"Неизвестная команда: {command}")
