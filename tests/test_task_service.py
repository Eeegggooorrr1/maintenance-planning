from datetime import date

import pytest

from maintenance_planning.model import TaskStatus
from maintenance_planning.service import DeviceService, TaskService


def _device(services):
    device_service: DeviceService = services["devices"]
    return device_service.create(1, "Холодильник", "крупная техника")


def test_task_service_creates_and_sorts_tasks(services) -> None:
    service: TaskService = services["tasks"]
    device = _device(services)
    service.create(
        1, device.id, "Поздняя задача", date(2026, 10, 1), priority=3
    )
    service.create(1, device.id, "Ранняя задача", date(2026, 9, 1), priority=1)

    tasks = service.list_for_user(1)

    assert [task.title for task in tasks] == [
        "Ранняя задача",
        "Поздняя задача",
    ]


def test_task_service_requires_owned_device(services) -> None:
    service: TaskService = services["tasks"]
    device = _device(services)

    with pytest.raises(KeyError):
        service.create(2, device.id, "Чужая задача", date(2026, 9, 1))


def test_complete_task_updates_device_and_status(services) -> None:
    task_service: TaskService = services["tasks"]
    device_service: DeviceService = services["devices"]
    device = _device(services)
    task = task_service.create(
        1, device.id, "Проверка фильтра", date(2026, 9, 1)
    )

    completed = task_service.complete(task.id, 1)

    assert completed.status == TaskStatus.COMPLETED
    assert completed.completed_at == date.today()
    assert device_service.list_for_user(1)[0].last_service_date == date.today()


def test_cancel_task_changes_status_and_blocks_other_user(services) -> None:
    task_service: TaskService = services["tasks"]
    device = _device(services)
    task = task_service.create(
        1, device.id, "Отменяемая задача", date(2026, 9, 1)
    )

    cancelled = task_service.cancel(task.id, 1)

    assert cancelled.status == TaskStatus.CANCELLED
    with pytest.raises(KeyError):
        task_service.cancel(task.id, 2)
