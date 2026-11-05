from contextlib import suppress
from datetime import date

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from devices.models import Device
from maintenance_tasks.models import Task
from maintenance_web.queries import (
    due_tasks,
    find_task,
    list_tasks,
    statistics,
)

SORT_FIELDS = {
    "date": "scheduled_date",
    "-date": "-scheduled_date",
    "priority": "priority",
    "device": "device__name",
}
PAGE_SIZE = 5


def _filter_device(queryset, value: str, errors: list[str]):
    if not value:
        return queryset
    if (
        len(value) <= 19
        and value.isascii()
        and value.isdigit()
        and 0 < int(value) < 2**63
    ):
        return queryset.filter(device_id=int(value))
    errors.append("Укажите корректный ID устройства.")
    return queryset


def tasks(request: HttpRequest) -> HttpResponse:
    queryset = list_tasks()
    errors = []
    selected = {
        key: request.GET.get(key, "").strip()
        for key in ("q", "until", "device", "status", "sort")
    }
    if selected["q"]:
        queryset = queryset.filter(
            Q(title__icontains=selected["q"])
            | Q(device__name__icontains=selected["q"])
        )
    if selected["until"]:
        try:
            until = date.fromisoformat(selected["until"])
        except ValueError:
            errors.append("Укажите корректную дату.")
        else:
            queryset = queryset.filter(scheduled_date__lte=until)
    queryset = _filter_device(queryset, selected["device"], errors)
    if selected["status"]:
        if selected["status"] in Task.Status.values:
            queryset = queryset.filter(status=selected["status"])
        else:
            errors.append("Неизвестный статус задачи.")
    sort = selected["sort"] or "date"
    if sort not in SORT_FIELDS:
        errors.append("Неизвестный способ сортировки.")
        sort = "date"
    selected["sort"] = sort
    if errors:
        queryset = queryset.none()
    queryset = queryset.order_by(SORT_FIELDS[sort], "pk")
    page = Paginator(queryset, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(
        request,
        "maintenance_tasks/task_list.html",
        {
            "tasks": page.object_list,
            "page_obj": page,
            "filters": selected,
            "errors": errors,
            "device_options": Device.objects.all(),
            "status_options": Task.Status.choices,
        },
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
