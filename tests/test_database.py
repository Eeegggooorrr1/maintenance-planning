import sqlite3

from db.import_json import import_data
from db.queries import (
    due_tasks,
    find_device,
    find_task,
    list_devices,
    list_tasks,
)


def test_json_import_creates_related_sqlite_data(tmp_path) -> None:
    source = tmp_path / "data"
    source.mkdir()
    source.joinpath("users.json").write_text(
        '[{"id": 1, "name": "Иван", "email": "ivan@example.com", '
        '"role": "user"}]',
        encoding="utf-8",
    )
    source.joinpath("devices.json").write_text(
        '[{"id": 1, "owner_id": 1, "name": "Чайник", '
        '"category": "малая техника", "brand": "A", "model": "B", '
        '"serial_number": "", "last_service_date": null, '
        '"service_interval_days": 180, "notes": ""}]',
        encoding="utf-8",
    )
    source.joinpath("tasks.json").write_text(
        '[{"id": 1, "owner_id": 1, "device_id": 1, "title": "Проверить", '
        '"scheduled_date": "2026-10-01", "description": "", '
        '"priority": 1, "status": "planned", "completed_at": null}]',
        encoding="utf-8",
    )
    database = tmp_path / "maintenance.sqlite"

    import_data(source, database)

    connection = sqlite3.connect(database)
    assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
    assert (
        connection.execute("SELECT COUNT(*) FROM devices").fetchone()[0] == 1
    )
    assert connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 1
    connection.close()


def test_sql_queries_return_named_related_results(
    tmp_path, monkeypatch
) -> None:
    database = tmp_path / "maintenance.sqlite"
    from db.import_json import import_data

    source = tmp_path / "data"
    source.mkdir()
    for name, content in {
        "users.json": (
            '[{"id": 1, "name": "Иван", "email": "ivan@example.com", '
            '"role": "user"}]'
        ),
        "devices.json": (
            '[{"id": 1, "owner_id": 1, "name": "Чайник", '
            '"category": "малая техника", "brand": "A", "model": "B", '
            '"serial_number": "", "last_service_date": null, '
            '"service_interval_days": 180, "notes": ""}]'
        ),
        "tasks.json": (
            '[{"id": 1, "owner_id": 1, "device_id": 1, '
            '"title": "Проверить", "scheduled_date": "2026-10-01", '
            '"description": "", "priority": 1, "status": "planned", '
            '"completed_at": null}]'
        ),
    }.items():
        source.joinpath(name).write_text(content, encoding="utf-8")
    import_data(source, database)
    monkeypatch.setattr("django.conf.settings.MAINTENANCE_DB_PATH", database)

    assert list_devices()[0]["name"] == "Чайник"
    assert list_tasks()[0]["device_name"] == "Чайник"
    assert find_device(1)["model"] == "B"
    assert find_task(1)["title"] == "Проверить"
    assert len(due_tasks("2026-10-02")) == 1
