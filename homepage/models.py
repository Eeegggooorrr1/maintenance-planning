from django.db import models


class User(models.Model):
    name = models.CharField(verbose_name="Имя", max_length=150)
    email = models.EmailField(verbose_name="Электронная почта", unique=True)
    role = models.CharField(
        verbose_name="Роль",
        max_length=10,
        choices=[("user", "Пользователь"), ("admin", "Администратор")],
        default="user",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["name", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=["user", "admin"]),
                name="valid_user_role",
            )
        ]

    def __str__(self) -> str:
        return self.name
