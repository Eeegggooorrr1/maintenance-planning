from datetime import date

from django.db.models import Count, QuerySet

from devices.models import Device
from maintenance_tasks.models import Task


def list_devices() -> QuerySet:
    return Device.objects.select_related("owner").all()


def find_device(device_id: int) -> Device | None:
    return list_devices().filter(pk=device_id).first()


def list_tasks() -> QuerySet:
    return Task.objects.select_related("device", "owner").all()


def find_task(task_id: int) -> Task | None:
    return list_tasks().filter(pk=task_id).first()


def due_tasks(until: str | date) -> QuerySet:
    return (
        list_tasks()
        .exclude(status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED])
        .filter(scheduled_date__lte=until)
    )


def statistics() -> tuple[QuerySet, QuerySet]:
    return (
        Device.objects.annotate(task_count=Count("tasks")).order_by(
            "name", "pk"
        ),
        Task.objects.values("status")
        .annotate(task_count=Count("pk"))
        .order_by("status"),
    )
