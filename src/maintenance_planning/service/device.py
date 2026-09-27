from datetime import date

from ..model import Device
from ..repo import DeviceRepository


class DeviceService:
    def __init__(
        self, repository: DeviceRepository, default_interval_days: int = 180
    ) -> None:
        self.repository = repository
        self.default_interval_days = default_interval_days

    def list_for_user(self, user_id: int) -> list[Device]:
        return self.repository.find_by_owner(user_id)

    def create(
        self, owner_id: int, name: str, category: str, **attributes
    ) -> Device:
        attributes.setdefault(
            "service_interval_days", self.default_interval_days
        )
        device = Device(
            self.repository.next_id(), owner_id, name, category, **attributes
        )
        return self.repository.create(device)

    def update(self, device: Device, user_id: int) -> Device:
        self._owned(device.id, user_id)
        return self.repository.update(device)

    def delete(self, device_id: int, user_id: int) -> None:
        self._owned(device_id, user_id)
        self.repository.delete(device_id)

    def mark_serviced(
        self,
        device_id: int,
        user_id: int,
        serviced_on: date | None = None,
    ) -> Device:
        device = self._owned(device_id, user_id)
        device.mark_serviced(serviced_on)
        return self.repository.update(device)

    def _owned(self, device_id: int, user_id: int) -> Device:
        device = self.repository.find_by_id(device_id)
        if device is None or device.owner_id != user_id:
            raise KeyError("Устройство не найдено")
        return device
