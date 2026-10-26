from contextlib import suppress
from datetime import date

from db.queries import due_tasks, find_task, list_tasks, statistics
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def tasks(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "maintenance_tasks/task_list.html",
        {"tasks": list_tasks()},
    )


def task_detail(
    request: HttpRequest,
    task_id: int,
) -> HttpResponse:
    task = find_task(task_id)
    return render(
        request,
        "maintenance_tasks/task_detail.html",
        {"task": task},
        status=404 if task is None else 200,
    )


def due_search(request: HttpRequest) -> HttpResponse:
    raw_date = request.GET.get("until", "")
    selected_date = ""
    if raw_date:
        with suppress(ValueError):
            selected_date = date.fromisoformat(raw_date).isoformat()
    return render(
        request,
        "maintenance_tasks/due_search.html",
        {
            "selected_date": selected_date,
            "invalid_date": bool(raw_date and not selected_date),
            "tasks": due_tasks(selected_date) if selected_date else None,
        },
    )


def task_statistics(request: HttpRequest) -> HttpResponse:
    by_device, by_status = statistics()
    return render(
        request,
        "maintenance_tasks/statistics.html",
        {"by_device": by_device, "by_status": by_status},
    )
