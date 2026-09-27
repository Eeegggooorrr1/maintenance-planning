from pathlib import Path

import pytest

from maintenance_planning.repo import (
    DeviceRepository,
    TaskRepository,
    UserRepository,
)
from maintenance_planning.service import (
    AuthService,
    DeviceService,
    TaskService,
)


@pytest.fixture
def repositories(tmp_path: Path) -> dict[str, object]:
    devices = DeviceRepository(tmp_path / "devices.json")
    tasks = TaskRepository(tmp_path / "tasks.json")
    users = UserRepository(tmp_path / "users.json")
    return {"devices": devices, "tasks": tasks, "users": users}


@pytest.fixture
def services(repositories: dict[str, object]) -> dict[str, object]:
    devices = repositories["devices"]
    tasks = repositories["tasks"]
    return {
        "auth": AuthService(repositories["users"]),
        "devices": DeviceService(devices),
        "tasks": TaskService(tasks, devices),
    }
