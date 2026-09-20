from datetime import date

import pytest

from maintenance_planning.service import (
    get_current_tasks,
    get_overdue_tasks,
    get_service_status,
    save_tasks,
    schedule_next_service,
)


def test_schedule_next_service() -> None:
    result = schedule_next_service(
        date(2026, 6, 10),
        180,
    )

    assert result == date(2026, 12, 7)


def test_schedule_next_service_rejects_bad_interval() -> None:
    with pytest.raises(ValueError):
        schedule_next_service(
            date(2026, 6, 10),
            0,
        )


def test_get_service_status_for_overdue_task() -> None:
    result = get_service_status(
        "Холодильник",
        date(2026, 9, 15),
        date(2026, 9, 20),
    )

    assert result == (
        "Обслуживание устройства «Холодильник» " "просрочено на 5 дн."
    )


def test_get_current_tasks_filters_and_sorts(tmp_path) -> None:
    file_path = tmp_path / "tasks.json"

    tasks = [
        {
            "device_name": "Пылесос",
            "service_date": date(2026, 9, 25),
            "done": False,
        },
        {
            "device_name": "Холодильник",
            "service_date": date(2026, 9, 15),
            "done": False,
        },
        {
            "device_name": "Микроволновка",
            "service_date": date(2026, 9, 10),
            "done": True,
        },
    ]

    save_tasks(file_path, tasks)

    result = get_current_tasks(file_path)

    assert len(result) == 2
    assert result[0]["device_name"] == "Холодильник"
    assert result[1]["device_name"] == "Пылесос"


def test_get_overdue_tasks_uses_service_layer(tmp_path) -> None:
    file_path = tmp_path / "tasks.json"

    tasks = [
        {
            "device_name": "Холодильник",
            "service_date": date(2026, 9, 15),
            "done": False,
        },
        {
            "device_name": "Стиральная машина",
            "service_date": date(2026, 9, 25),
            "done": False,
        },
        {
            "device_name": "Пылесос",
            "service_date": date(2026, 9, 10),
            "done": True,
        },
    ]

    save_tasks(file_path, tasks)

    result = get_overdue_tasks(
        file_path,
        date(2026, 9, 20),
    )

    assert len(result) == 1
    assert result[0]["device_name"] == "Холодильник"
