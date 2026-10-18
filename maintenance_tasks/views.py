from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from maintenance_web.repositories import (
    get_device_repository,
    get_task_repository,
)


def tasks(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "maintenance_tasks/task_list.html",
        {"tasks": get_task_repository().list_all()},
    )


def task_detail(
    request: HttpRequest,
    task_id: int,
) -> HttpResponse:
    task = get_task_repository().find_by_id(task_id)
    device = (
        get_device_repository().find_by_id(task.device_id) if task else None
    )
    return render(
        request,
        "maintenance_tasks/task_detail.html",
        {"task": task, "device": device},
        status=404 if task is None else 200,
    )
