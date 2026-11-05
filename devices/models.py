from datetime import date, timedelta

from django.core.validators import MinValueValidator
from django.db import models


class Device(models.Model):
    owner = models.ForeignKey(
        "homepage.User", on_delete=models.PROTECT, related_name="devices"
    )
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    service_interval_days = models.PositiveIntegerField(
        default=180, validators=[MinValueValidator(1)]
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(service_interval_days__gt=0),
                name="positive_service_interval",
            )
        ]

    @property
    def next_service_date(self) -> date | None:
        if self.last_service_date is None:
            return None
        return self.last_service_date + timedelta(
            days=self.service_interval_days
        )

    def __str__(self) -> str:
        return self.name
