from functools import lru_cache

from django.conf import settings

from maintenance_planning.repo import DeviceRepository, TaskRepository


@lru_cache
def get_device_repository() -> DeviceRepository:
    return DeviceRepository(settings.APP_SETTINGS.data_dir / "devices.json")


@lru_cache
def get_task_repository() -> TaskRepository:
    return TaskRepository(settings.APP_SETTINGS.data_dir / "tasks.json")
