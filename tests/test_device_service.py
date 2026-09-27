import pytest

from maintenance_planning.service import DeviceService


def test_device_service_creates_lists_updates_and_deletes(services) -> None:
    service: DeviceService = services["devices"]
    device = service.create(1, "Пылесос", "малая техника", brand="Bosch")

    assert service.list_for_user(1) == [device]
    assert service.list_for_user(2) == []

    device.name = "Робот-пылесос"
    service.update(device, 1)
    assert service.list_for_user(1)[0].name == "Робот-пылесос"

    service.delete(device.id, 1)
    assert service.list_for_user(1) == []


def test_device_service_does_not_allow_other_owner(services) -> None:
    service: DeviceService = services["devices"]
    device = service.create(1, "Холодильник", "крупная техника")

    with pytest.raises(KeyError):
        service.update(device, 2)
    with pytest.raises(KeyError):
        service.delete(device.id, 2)


def test_device_service_marks_service_date(services) -> None:
    from datetime import date

    service: DeviceService = services["devices"]
    device = service.create(1, "Стиральная машина", "крупная техника")

    updated = service.mark_serviced(device.id, 1, date(2026, 9, 25))

    assert updated.last_service_date == date(2026, 9, 25)
