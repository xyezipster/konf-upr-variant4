"""Точка входа консольного приложения."""

from .shell import Shell


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


def main():
    """Запустить минимальный прототип."""
    repl(Shell())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
