import json
from pathlib import Path
from typing import Any


def load_data(file_path: str | Path) -> list[dict[str, Any]]:
    """Загружает список записей из JSON-файла."""
    path = Path(file_path)

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError("Некорректный JSON-файл") from error

    if not isinstance(data, list):
        raise ValueError("JSON-файл должен содержать список")

    return data


def save_data(
    file_path: str | Path,
    data: list[dict[str, Any]],
) -> None:
    """Сохраняет список записей в JSON-файл."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4,
            )
    except OSError as error:
        raise OSError("Не удалось сохранить данные") from error
