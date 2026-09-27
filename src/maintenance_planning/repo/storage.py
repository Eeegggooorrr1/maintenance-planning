import json
from pathlib import Path
from typing import Any


class JsonStorage:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"Некорректный JSON-файл: {self.path}") from error
        if not isinstance(value, list):
            raise ValueError("JSON-файл должен содержать список")
        return value

    def write(self, rows: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=4), encoding="utf-8"
        )
