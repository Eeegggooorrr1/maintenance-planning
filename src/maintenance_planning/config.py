import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path
    app_name: str = "Система планирования обслуживания бытовой техники"
    default_service_interval_days: int = 180

    @classmethod
    def from_env(cls, env_file: str | Path | None = None) -> "Settings":
        values: dict[str, str] = {}
        path = Path(env_file or ".env")
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    values[key.strip()] = value.strip().strip("\"'")
        values.update(
            {
                key: value
                for key, value in os.environ.items()
                if key.startswith("MAINTENANCE_")
            }
        )
        data_dir = Path(
            values.get("MAINTENANCE_DATA_DIR", "src/maintenance_planning/data")
        )
        return cls(
            data_dir=data_dir,
            app_name=values.get("MAINTENANCE_APP_NAME", cls.app_name),
            default_service_interval_days=int(
                values.get(
                    "MAINTENANCE_SERVICE_INTERVAL",
                    cls.default_service_interval_days,
                )
            ),
        )
