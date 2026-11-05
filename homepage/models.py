from django.db import models


class User(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=[("user", "Пользователь"), ("admin", "Администратор")],
        default="user",
    )

    class Meta:
        ordering = ["name", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=["user", "admin"]),
                name="valid_user_role",
            )
        ]

    def __str__(self) -> str:
        return self.name
