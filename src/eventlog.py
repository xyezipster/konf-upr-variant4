"""JSON-журнал вызовов команд с именем пользователя."""

import getpass
import json
from datetime import datetime, timezone


class EventLog:
    """Хранить события в JSON-массиве, дополняя существующий журнал."""

    def __init__(self, path=None):
        """Загрузить прежние события и проверить доступность файла."""
        self.path = path
        self.events = []
        if path is not None:
            if path.exists():
                self.events = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(self.events, list):
                    raise ValueError("Журнал должен содержать JSON-массив")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
            self._save()

    def record(self, command, result):
        """Сохранить вызов, пользователя, время и результат команды."""
        if self.path is None:
            return
        self.events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": getpass.getuser(),
            "command": command,
            "output": result.output,
            "status": "error" if result.error else "ok",
            "exit": result.stop,
        })
        self._save()

    def _save(self):
        """Записать корректный JSON после каждого вызова команды."""
        self.path.write_text(json.dumps(self.events, ensure_ascii=False,
                                       indent=2) + "\n", encoding="utf-8")
