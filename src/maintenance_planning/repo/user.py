from dataclasses import asdict
from pathlib import Path

from ..model import User, UserRole
from .storage import JsonStorage


class UserRepository:
    def __init__(self, path: str | Path) -> None:
        self.storage = JsonStorage(path)

    def find_by_id(self, user_id: int) -> User | None:
        return next(
            (user for user in self.list_all() if user.id == user_id), None
        )

    def find_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        return next(
            (user for user in self.list_all() if user.email == normalized),
            None,
        )

    def list_all(self) -> list[User]:
        return [
            User(**{**row, "role": UserRole(row.get("role", "user"))})
            for row in self.storage.read()
        ]

    def create(self, user: User) -> User:
        rows = self.list_all()
        if self.find_by_email(user.email):
            raise ValueError("Пользователь с таким email уже существует")
        rows.append(user)
        self._save(rows)
        return user

    def update(self, user: User) -> User:
        rows = self._replace(user)
        self._save(rows)
        return user

    def delete(self, user_id: int) -> None:
        self._save([user for user in self.list_all() if user.id != user_id])

    def next_id(self) -> int:
        return max((user.id for user in self.list_all()), default=0) + 1

    def _replace(self, updated: User) -> list[User]:
        rows = self.list_all()
        if not any(user.id == updated.id for user in rows):
            raise KeyError("Пользователь не найден")
        return [updated if user.id == updated.id else user for user in rows]

    def _save(self, users: list[User]) -> None:
        self.storage.write(
            [{**asdict(user), "role": user.role.value} for user in users]
        )
