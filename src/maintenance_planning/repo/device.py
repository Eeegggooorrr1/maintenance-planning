
from dataclasses import asdict
from datetime import date
from pathlib import Path

from ..model import Device
from .storage import JsonStorage


class DeviceRepository:
    def __init__(self, path: str | Path) -> None:
        self.storage = JsonStorage(path)

    def find_by_id(self, device_id: int) -> Device | None:
        return next(
            (device for device in self.list_all() if device.id == device_id),
            None,
        )

    def find_by_owner(self, owner_id: int) -> list[Device]:
        return [
            device for device in self.list_all() if device.owner_id == owner_id
        ]

    def list_all(self) -> list[Device]:
        return [self._from_row(row) for row in self.storage.read()]

    def create(self, device: Device) -> Device:
        rows = self.list_all()
        rows.append(device)
        self._save(rows)
        return device

    def update(self, device: Device) -> Device:
        rows = self.list_all()
        if not any(item.id == device.id for item in rows):
            raise KeyError("Устройство не найдено")
        self._save([device if item.id == device.id else item for item in rows])
        return device

    def delete(self, device_id: int) -> None:
        self._save([item for item in self.list_all() if item.id != device_id])

    def next_id(self) -> int:
        return max((device.id for device in self.list_all()), default=0) + 1

    @staticmethod
    def _from_row(row: dict) -> Device:
        if row.get("last_service_date"):
            row = {
                **row,
                "last_service_date": date.fromisoformat(
                    row["last_service_date"]
                ),
            }
        return Device(**row)

    def _save(self, devices: list[Device]) -> None:
        rows = []
        for device in devices:
            row = asdict(device)
            if device.last_service_date:
                row["last_service_date"] = device.last_service_date.isoformat()
            rows.append(row)
        self.storage.write(rows)
