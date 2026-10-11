from html import escape

from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from homepage.views import page
from maintenance_web.repositories import (
    get_device_repository,
    get_task_repository,
)

STATUS_LABELS = {
    "planned": "запланировано",
    "in_progress": "в работе",
    "completed": "выполнено",
    "cancelled": "отменено",
}


def tasks(request: HttpRequest) -> HttpResponse:
    items = ""
    for task in get_task_repository().list_all():
        status = STATUS_LABELS[task.status.value]
        items += (
            '<a class="list-group-item list-group-item-action" '
            f'href="{reverse("maintenance_tasks:detail", args=[task.id])}">'
            f"{escape(task.title)} - {task.scheduled_date} - {status}"
            "</a>"
        )
    content = f"""
    <h1>Задачи обслуживания</h1>
    <div class="list-group">{items}</div>
    """
    return HttpResponse(page("ТехСервис - задачи", content))


def task_detail(
    request: HttpRequest,
    task_id: int,
) -> HttpResponse:
    list_url = reverse("maintenance_tasks:list")
    task = get_task_repository().find_by_id(task_id)
    if task is None:
        content = f"""
        <h1 class="text-danger">Задача не найдена</h1>
        <a href="{list_url}" class="btn btn-outline-secondary">
            К списку задач
        </a>
        """
        return HttpResponse(
            page("Задача не найдена", content),
            status=404,
        )

    device = get_device_repository().find_by_id(task.device_id)
    device_name = escape(device.name) if device else "устройство не найдено"
    status = STATUS_LABELS[task.status.value]
    content = f"""
    <div class="card">
        <div class="card-body">
            <h1 class="card-title">{escape(task.title)}</h1>
            <p><strong>ID:</strong> {task.id}</p>
            <p><strong>Устройство:</strong> {device_name}</p>
            <p><strong>Дата:</strong> {task.scheduled_date}</p>
            <p><strong>Приоритет:</strong> {task.priority}</p>
            <p><strong>Статус:</strong> {status}</p>
            <a href="{list_url}" class="btn btn-outline-secondary">
                К списку задач
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(task.title, content))
