from datetime import date
from pathlib import Path

from service import (
    get_current_tasks,
    get_overdue_tasks,
    get_service_status,
    schedule_next_service,
)

DATA_FILE = Path(__file__).parent / "data" / "tasks.json"


def main() -> None:
    """Запускает основной сценарий программы."""
    current_date = date.today()

    try:
        tasks = get_current_tasks(
            DATA_FILE,
        )

        overdue_tasks = get_overdue_tasks(
            DATA_FILE,
            current_date,
        )
    except (OSError, ValueError) as error:
        print(f"Ошибка работы с данными: {error}")
        return

    print("Система планирования обслуживания бытовой техники")
    print(f"Дата проверки: {current_date}\n")

    for task in tasks:
        print(
            get_service_status(
                str(task["device_name"]),
                task["service_date"],
                current_date,
            )
        )

    print(f"\nПросроченных задач: {len(overdue_tasks)}")

    for task in overdue_tasks:
        print(f"- {task['device_name']} " f"(срок: {task['service_date']})")
    next_service = schedule_next_service(
        date(2026, 6, 10),
        180,
    )

    print(f"\nСледующее обслуживание рассчитано на: " f"{next_service}")


if __name__ == "__main__":
    main()
