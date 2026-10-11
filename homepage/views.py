from html import escape

from django.http import HttpRequest, HttpResponse
from django.urls import reverse

BOOTSTRAP_URL = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/"
    "dist/css/bootstrap.min.css"
)


def page(title: str, content: str) -> str:
    home_url = reverse("homepage:index")
    devices_url = reverse("devices:list")
    tasks_url = reverse("maintenance_tasks:list")
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="{BOOTSTRAP_URL}">
</head>
<body>
    <nav class="navbar navbar-expand bg-dark mb-4" data-bs-theme="dark">
        <div class="container">
            <a class="navbar-brand" href="{home_url}">ТехСервис</a>
            <div class="navbar-nav">
                <a class="nav-link" href="{devices_url}">Устройства</a>
                <a class="nav-link" href="{tasks_url}">Задачи</a>
            </div>
        </div>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def index(request: HttpRequest) -> HttpResponse:
    devices_url = reverse("devices:list")
    tasks_url = reverse("maintenance_tasks:list")
    content = f"""
    <h1 class="display-5">Планирование обслуживания техники</h1>
    <p class="lead">Контроль устройств и плановых работ в браузере.</p>
    <a href="{devices_url}" class="btn btn-primary me-2">Устройства</a>
    <a href="{tasks_url}" class="btn btn-secondary">Задачи</a>
    """
    return HttpResponse(page("ТехСервис", content))


def page_not_found(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    home_url = reverse("homepage:index")
    content = f"""
    <h1 class="text-danger">404 - страница не найдена</h1>
    <p>Проверьте адрес или вернитесь на главную страницу.</p>
    <a href="{home_url}" class="btn btn-primary">На главную</a>
    """
    return HttpResponse(
        page("Страница не найдена", content),
        status=404,
    )
