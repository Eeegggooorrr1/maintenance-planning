from maintenance_planning.service import AuthService


def test_login_or_create_creates_user_once(services) -> None:
    auth: AuthService = services["auth"]

    first = auth.login_or_create("Анна", "ANNA@example.com")
    second = auth.login_or_create("Другое имя", "anna@example.com")

    assert first.id == second.id
    assert second.name == "Анна"
    assert second.email == "anna@example.com"


def test_login_or_create_rejects_invalid_email(services) -> None:
    auth: AuthService = services["auth"]

    try:
        auth.login_or_create("Анна", "invalid-email")
    except ValueError as error:
        assert "email" in str(error)
    else:
        raise AssertionError("Ожидалась ошибка валидации email")
