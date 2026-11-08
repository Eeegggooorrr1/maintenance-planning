from datetime import date, timedelta
from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


def device_slug() -> str:
    return f"device-{uuid4().hex}"


class Device(models.Model):
    slug = models.SlugField(
        "Адрес страницы", unique=True, default=device_slug, editable=False
    )

    owner = models.ForeignKey(
        "homepage.User",
        verbose_name="Владелец",
        on_delete=models.PROTECT,
        related_name="devices",
    )
    name = models.CharField(verbose_name="Название", max_length=200)
    category = models.CharField(verbose_name="Категория", max_length=100)
    brand = models.CharField(verbose_name="Бренд", max_length=100, blank=True)
    model = models.CharField(verbose_name="Модель", max_length=100, blank=True)
    serial_number = models.CharField(
        verbose_name="Серийный номер", max_length=100, blank=True
    )
    last_service_date = models.DateField(
        verbose_name="Последнее обслуживание", null=True, blank=True
    )
    service_interval_days = models.PositiveIntegerField(
        verbose_name="Интервал обслуживания в днях",
        default=180,
        validators=[MinValueValidator(1)],
    )
    notes = models.TextField(verbose_name="Примечания", blank=True)

    class Meta:
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"
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

    def get_absolute_url(self) -> str:
        return reverse("devices:detail_slug", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        return self.name
