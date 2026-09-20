from datetime import date, timedelta
from pathlib import Path

from . import repository

Task = dict[str, str | bool | date]


def schedule_next_service(
    last_service_date: date,
    interval_days: int,
) -> date:
    """Считает дату следующего обслуживания."""
    if interval_days <= 0:
        raise ValueError("Интервал обслуживания должен быть положительным")

    return last_service_date + timedelta(days=interval_days)


def get_service_status(
    device_name: str,
    service_date: date,
    current_date: date,
) -> str:
    """Возвращает статус обслуживания устройства."""
    days_until_service = (service_date - current_date).days

    if days_until_service < 0:
        return (
            f"Обслуживание устройства «{device_name}» просрочено "
            f"на {abs(days_until_service)} дн."
        )

    if days_until_service == 0:
        return (
            "Сегодня необходимо выполнить обслуживание устройства "
            f"«{device_name}»"
        )

    return (
        f"Обслуживание устройства «{device_name}» запланировано "
        f"через {days_until_service} дн."
    )


def get_over_tasks(
    tasks: list[Task],
    current_date: date,
) -> list[Task]:
    """Возвращает невыполненные просроченные задачи."""
    return [
        task
        for task in tasks
        if not task["done"] and task["service_date"] < current_date
    ]


def sort_tasks_by_date(tasks: list[Task]) -> list[Task]:
    """Сортирует задачи по дате обслуживания."""
    return sorted(
        tasks,
        key=lambda task: task["service_date"],
    )


def load_tasks(file_path: str | Path) -> list[Task]:
    """Загружает задачи и преобразует даты в объекты date."""
    raw_tasks = repository.load_data(file_path)
    tasks: list[Task] = []

    for item in raw_tasks:
        if not isinstance(item.get("device_name"), str):
            raise ValueError("Некорректное название устройства")

        if not isinstance(item.get("done"), bool):
            raise ValueError("Поле done должно быть логическим")

        try:
            service_date = date.fromisoformat(str(item["service_date"]))
        except (KeyError, ValueError) as error:
            raise ValueError("Некорректная дата обслуживания") from error

        tasks.append(
            {
                "device_name": item["device_name"],
                "service_date": service_date,
                "done": item["done"],
            }
        )

    return tasks


def save_tasks(
    file_path: str | Path,
    tasks: list[Task],
) -> None:
    """Преобразует задачи и сохраняет их через репозиторий."""
    raw_tasks: list[dict[str, str | bool]] = []

    for task in tasks:
        service_date = task["service_date"]

        if not isinstance(service_date, date):
            raise ValueError("Дата обслуживания должна иметь тип date")

        raw_tasks.append(
            {
                "device_name": str(task["device_name"]),
                "service_date": service_date.isoformat(),
                "done": bool(task["done"]),
            }
        )

    repository.save_data(file_path, raw_tasks)


def get_current_tasks(
    file_path: str | Path,
) -> list[Task]:
    """Загружает и сортирует невыполненные задачи."""
    tasks = load_tasks(file_path)

    active_tasks = [task for task in tasks if not task["done"]]

    return sort_tasks_by_date(active_tasks)


def get_overdue_tasks(
    file_path: str | Path,
    current_date: date,
) -> list[Task]:
    """Загружает данные и возвращает просроченные задачи."""
    tasks = load_tasks(file_path)
    return get_over_tasks(tasks, current_date)
