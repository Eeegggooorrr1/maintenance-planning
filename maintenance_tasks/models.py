from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TaskQuerySet(models.QuerySet):
    def active(self):
        return self.filter(
            status__in=[Task.Status.PLANNED, Task.Status.IN_PROGRESS]
        )

    def cancelled(self):
        return self.filter(status=Task.Status.CANCELLED)

    def completed(self):
        return self.filter(status=Task.Status.COMPLETED)

    def for_date(self, selected_date):
        return self.filter(scheduled_date=selected_date)

    def with_related(self):
        return self.select_related("device", "owner")

    def for_list(self):
        return self.annotate(
            device_name=models.F("device__name"),
            device_slug=models.F("device__slug"),
            owner_name=models.F("owner__name"),
        ).values(
            "id",
            "title",
            "device_id",
            "device_name",
            "device_slug",
            "owner_name",
            "scheduled_date",
            "status",
            "priority",
        )


class Task(models.Model):
    objects = TaskQuerySet.as_manager()

    class Status(models.TextChoices):
        PLANNED = "planned", "Запланирована"
        IN_PROGRESS = "in_progress", "В работе"
        COMPLETED = "completed", "Завершена"
        CANCELLED = "cancelled", "Отменена"

    owner = models.ForeignKey(
        "homepage.User",
        verbose_name="Владелец",
        on_delete=models.PROTECT,
        related_name="tasks",
    )
    device = models.ForeignKey(
        "devices.Device",
        verbose_name="Устройство",
        on_delete=models.PROTECT,
        related_name="tasks",
    )
    title = models.CharField(verbose_name="Название", max_length=200)
    scheduled_date = models.DateField(
        verbose_name="Дата выполнения", db_index=True
    )
    description = models.TextField(verbose_name="Описание", blank=True)
    priority = models.PositiveSmallIntegerField(
        verbose_name="Приоритет",
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
    )
    status = models.CharField(
        verbose_name="Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    completed_at = models.DateTimeField(
        verbose_name="Дата завершения", null=True, blank=True
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи обслуживания"
        ordering = ["scheduled_date", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(priority__gte=1, priority__lte=3),
                name="valid_task_priority",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "planned",
                        "in_progress",
                        "completed",
                        "cancelled",
                    ]
                ),
                name="valid_task_status",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if (
            self.device_id
            and self.owner_id
            and self.device.owner_id != self.owner_id
        ):
            raise ValidationError(
                {
                    "owner": (
                        "Владелец задачи должен совпадать "
                        "с владельцем устройства."
                    )
                }
            )

    def __str__(self) -> str:
        return self.title
