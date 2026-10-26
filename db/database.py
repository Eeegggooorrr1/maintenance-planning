import sqlite3
from pathlib import Path

from django.conf import settings


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or settings.MAINTENANCE_DB_PATH
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
