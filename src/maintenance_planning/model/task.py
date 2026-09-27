from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class TaskStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Task:
    id: int
    owner_id: int
    device_id: int
    title: str
    scheduled_date: date
    description: str = ""
    priority: int = 2
    status: TaskStatus = TaskStatus.PLANNED
    completed_at: date | None = None

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Название задачи обязательно")
        if not 1 <= self.priority <= 3:
            raise ValueError("Приоритет должен быть от 1 до 3")

    @property
    def is_active(self) -> bool:
        return self.status in (TaskStatus.PLANNED, TaskStatus.IN_PROGRESS)

    def start(self) -> None:
        if self.status != TaskStatus.PLANNED:
            raise ValueError("Начать можно только запланированную задачу")
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, completed_on: date | None = None) -> None:
        if self.status == TaskStatus.CANCELLED:
            raise ValueError("Отмененную задачу нельзя завершить")
        self.status = TaskStatus.COMPLETED
        self.completed_at = completed_on or date.today()

    def cancel(self) -> None:
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Завершенную задачу нельзя отменить")
        self.status = TaskStatus.CANCELLED

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.title} на {self.scheduled_date} "
            f"({self.status.value}, приоритет {self.priority})"
        )
