from ..model import User
from ..repo import UserRepository


class AuthService:

    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def login_or_create(self, name: str, email: str) -> User:
        user = self.users.find_by_email(email)
        if user is not None:
            return user
        return self.users.create(User(self.users.next_id(), name, email))
