from dataclasses import asdict
from datetime import date
from pathlib import Path

from ..model import Task, TaskStatus
from .storage import JsonStorage


class TaskRepository:
    def __init__(self, path: str | Path) -> None:
        self.storage = JsonStorage(path)

    def find_by_id(self, task_id: int) -> Task | None:
        return next(
            (task for task in self.list_all() if task.id == task_id), None
        )

    def find_by_owner(
        self, owner_id: int, active_only: bool = False
    ) -> list[Task]:
        tasks = [task for task in self.list_all() if task.owner_id == owner_id]
        return (
            [task for task in tasks if task.is_active]
            if active_only
            else tasks
        )

    def list_all(self) -> list[Task]:
        return [self._from_row(row) for row in self.storage.read()]

    def create(self, task: Task) -> Task:
        rows = self.list_all()
        rows.append(task)
        self._save(rows)
        return task

    def update(self, task: Task) -> Task:
        rows = self.list_all()
        if not any(item.id == task.id for item in rows):
            raise KeyError("Задача не найдена")
        self._save([task if item.id == task.id else item for item in rows])
        return task

    def delete(self, task_id: int) -> None:
        self._save([item for item in self.list_all() if item.id != task_id])

    def next_id(self) -> int:
        return max((task.id for task in self.list_all()), default=0) + 1

    @staticmethod
    def _from_row(row: dict) -> Task:
        row = {
            **row,
            "scheduled_date": date.fromisoformat(row["scheduled_date"]),
        }
        if row.get("completed_at"):
            row["completed_at"] = date.fromisoformat(row["completed_at"])
        row["status"] = TaskStatus(row.get("status", "planned"))
        return Task(**row)

    def _save(self, tasks: list[Task]) -> None:
        rows = []
        for task in tasks:
            row = asdict(task)
            row["scheduled_date"] = task.scheduled_date.isoformat()
            row["completed_at"] = (
                task.completed_at.isoformat() if task.completed_at else None
            )
            row["status"] = task.status.value
            rows.append(row)
        self.storage.write(rows)
