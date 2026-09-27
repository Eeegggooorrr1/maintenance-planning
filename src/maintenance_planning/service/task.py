from datetime import date

from ..model import Task
from ..repo import DeviceRepository, TaskRepository


class TaskService:
    def __init__(
        self, tasks: TaskRepository, devices: DeviceRepository
    ) -> None:
        self.tasks = tasks
        self.devices = devices

    def list_for_user(
        self, user_id: int, active_only: bool = False
    ) -> list[Task]:
        tasks = self.tasks.find_by_owner(user_id, active_only)
        return sorted(
            tasks,
            key=lambda task: (task.scheduled_date, task.priority),
        )

    def create(
        self,
        owner_id: int,
        device_id: int,
        title: str,
        scheduled_date: date,
        **attributes,
    ) -> Task:
        device = self.devices.find_by_id(device_id)
        if device is None or device.owner_id != owner_id:
            raise KeyError("Устройство не найдено")
        task = Task(
            self.tasks.next_id(),
            owner_id,
            device_id,
            title,
            scheduled_date,
            **attributes,
        )
        return self.tasks.create(task)

    def complete(self, task_id: int, user_id: int) -> Task:
        task = self._owned(task_id, user_id)
        task.complete()
        device = self.devices.find_by_id(task.device_id)
        if device:
            device.mark_serviced(task.completed_at)
            self.devices.update(device)
        return self.tasks.update(task)

    def cancel(self, task_id: int, user_id: int) -> Task:
        task = self._owned(task_id, user_id)
        task.cancel()
        return self.tasks.update(task)

    def _owned(self, task_id: int, user_id: int) -> Task:
        task = self.tasks.find_by_id(task_id)
        if task is None or task.owner_id != user_id:
            raise KeyError("Задача не найдена")
        return task
