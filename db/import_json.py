import json
from pathlib import Path

from django.conf import settings

from .database import get_connection


def import_data(
    data_dir: Path | None = None,
    db_path: Path | None = None,
) -> None:
    source = data_dir or settings.APP_SETTINGS.data_dir
    target = db_path or settings.MAINTENANCE_DB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    schema = (settings.BASE_DIR / "sql" / "schema.sql").read_text(
        encoding="utf-8"
    )
    with get_connection(target) as connection:
        connection.executescript(schema)
        for table in ("users", "devices", "tasks"):
            rows = json.loads(
                (source / f"{table}.json").read_text(encoding="utf-8")
            )
            if not rows:
                continue
            columns = tuple(rows[0])
            placeholders = ", ".join("?" for _ in columns)
            column_names = ", ".join(columns)
            statement = (
                f"INSERT OR REPLACE INTO {table} ({column_names}) "
                f"VALUES ({placeholders})"
            )
            connection.executemany(
                statement,
                ([row[column] for column in columns] for row in rows),
            )


if __name__ == "__main__":
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maintenance_web.settings")
    django.setup()
    import_data()
