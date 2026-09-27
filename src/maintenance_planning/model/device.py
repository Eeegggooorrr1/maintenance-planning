from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(slots=True)
class Device:
    id: int
    owner_id: int
    name: str
    category: str
    brand: str = ""
    model: str = ""
    serial_number: str = ""
    last_service_date: date | None = None
    service_interval_days: int = 180
    notes: str = ""

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.category = self.category.strip()
        if not self.name or not self.category:
            raise ValueError("Название и категория устройства обязательны")
        if self.service_interval_days <= 0:
            raise ValueError("Интервал обслуживания должен быть положительным")

    @property
    def next_service_date(self) -> date | None:
        if self.last_service_date is None:
            return None
        return self.last_service_date + timedelta(
            days=self.service_interval_days
        )

    def mark_serviced(self, serviced_on: date | None = None) -> None:
        self.last_service_date = serviced_on or date.today()

    def __str__(self) -> str:
        details = " ".join(part for part in (self.brand, self.model) if part)
        return f"[{self.id}] {self.name} ({details or self.category})"
