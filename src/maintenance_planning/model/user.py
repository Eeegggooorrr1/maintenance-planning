from dataclasses import dataclass
from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


@dataclass(slots=True)
class User:
    id: int
    name: str
    email: str
    role: UserRole = UserRole.USER

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.email = self.email.strip().lower()
        if not self.name or "@" not in self.email:
            raise ValueError("Имя и корректный email обязательны")

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def __str__(self) -> str:
        return f"{self.name} ({self.email}, роль: {self.role.value})"
