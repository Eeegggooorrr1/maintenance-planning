import sqlite3
from contextlib import closing
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from devices.models import Device
from homepage.models import User
from maintenance_tasks.models import Task


class Command(BaseCommand):
    help = "Перенести данные из SQLite ПР7 без изменения исходной базы"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source", type=Path, default=settings.MAINTENANCE_DB_PATH
        )

    def handle(self, *args, **options):
        source = options["source"].resolve()
        if not source.is_file():
            raise CommandError(f"Исходная база не найдена: {source}")
        if source == Path(settings.DATABASES["default"]["NAME"]).resolve():
            raise CommandError("Исходная и целевая базы должны различаться.")
        try:
            with closing(
                sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
            ) as connection:
                connection.row_factory = sqlite3.Row
                rows = {
                    table: [
                        dict(row)
                        for row in connection.execute(f"SELECT * FROM {table}")
                    ]
                    for table in ("users", "devices", "tasks")
                }
            with transaction.atomic():
                if any(
                    model.objects.exists() for model in (User, Device, Task)
                ):
                    raise CommandError(
                        (
                            "Целевые таблицы не пусты. "
                            "Перенос отменён без изменений."
                        )
                    )
                for model, table in (
                    (User, "users"),
                    (Device, "devices"),
                    (Task, "tasks"),
                ):
                    for row in rows[table]:
                        obj = model(**row)
                        obj.full_clean()
                        obj.save(force_insert=True)
                    if model.objects.count() != len(rows[table]):
                        raise CommandError(
                            f"Не совпало количество записей: {table}"
                        )
        except CommandError:
            raise
        except Exception as exc:
            raise CommandError(f"Перенос отменён: {exc}") from exc
        self.stdout.write(
            self.style.SUCCESS(
                "Перенесено: "
                + ", ".join(
                    f"{table}={len(data)}" for table, data in rows.items()
                )
            )
        )
