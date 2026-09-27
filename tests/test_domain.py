from datetime import date

import pytest

from maintenance_planning.model import Device, Task, TaskStatus


def test_device_calculates_next_service_and_can_be_serviced() -> None:
    device = Device(
        1,
        10,
        "Холодильник",
        "кухонная техника",
        last_service_date=date(2026, 1, 1),
    )
    assert device.next_service_date == date(2026, 6, 30)
    device.mark_serviced(date(2026, 2, 1))
    assert device.last_service_date == date(2026, 2, 1)


def test_task_state_transition_rejects_cancelled_completion() -> None:
    task = Task(1, 1, 1, "Проверка", date(2026, 9, 25))
    task.cancel()
    assert task.status == TaskStatus.CANCELLED
    with pytest.raises(ValueError):
        task.complete()
