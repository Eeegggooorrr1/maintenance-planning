from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Task(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Запланирована"
        IN_PROGRESS = "in_progress", "В работе"
        COMPLETED = "completed", "Завершена"
        CANCELLED = "cancelled", "Отменена"

    owner = models.ForeignKey(
        "homepage.User", on_delete=models.PROTECT, related_name="tasks"
    )
    device = models.ForeignKey(
        "devices.Device", on_delete=models.PROTECT, related_name="tasks"
    )
    title = models.CharField(max_length=200)
    scheduled_date = models.DateField(db_index=True)
    description = models.TextField(blank=True)
    priority = models.PositiveSmallIntegerField(
        default=2, validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
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
