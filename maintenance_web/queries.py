from datetime import date

from django.db.models import Count, Q, QuerySet

from devices.models import Device
from maintenance_tasks.models import Task


def list_devices() -> QuerySet:
    return Device.objects.select_related("owner").all()


def find_device(device_id: int) -> Device | None:
    return list_devices().filter(pk=device_id).first()


def list_tasks() -> QuerySet:
    return Task.objects.with_related()


def find_task(task_id: int) -> Task | None:
    return list_tasks().filter(pk=task_id).first()


def due_tasks(until: str | date) -> QuerySet:
    return list_tasks().active().filter(scheduled_date__lte=until)


def statistics() -> tuple[QuerySet, QuerySet]:
    return (
        Device.objects.annotate(task_count=Count("tasks")).order_by(
            "name", "pk"
        ),
        Task.objects.values("status")
        .annotate(task_count=Count("pk"))
        .order_by("status"),
    )


def task_totals() -> dict:
    return Task.objects.aggregate(
        total=Count("pk"),
        active=Count(
            "pk",
            filter=Q(
                status__in=[Task.Status.PLANNED, Task.Status.IN_PROGRESS]
            ),
        ),
        completed=Count("pk", filter=Q(status=Task.Status.COMPLETED)),
        cancelled=Count("pk", filter=Q(status=Task.Status.CANCELLED)),
    )


def devices_without_tasks_on(selected_date: date) -> QuerySet:
    occupied = (
        Task.objects.active()
        .for_date(selected_date)
        .values_list("device_id", flat=True)
    )
    return list_devices().exclude(pk__in=occupied)
