from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from maintenance_web.queries import (
    devices_without_tasks_on,
    find_device,
    list_devices,
)

from .models import Device


def devices(request: HttpRequest) -> HttpResponse:
    available_on = request.GET.get("available_on", "")
    queryset = list_devices()
    error = ""
    if available_on:
        try:
            selected = date.fromisoformat(available_on)
        except ValueError:
            error = "Укажите корректную дату."
            queryset = queryset.none()
        else:
            queryset = devices_without_tasks_on(selected)
    return render(
        request,
        "devices/device_list.html",
        {
            "devices": queryset,
            "available_on": available_on,
            "error": error,
        },
    )


def device_detail(
    request: HttpRequest,
    device_id: int,
) -> HttpResponse:
    device = find_device(device_id)
    return render(
        request,
        "devices/device_detail.html",
        {"device": device},
        status=404 if device is None else 200,
    )


def device_by_slug(request: HttpRequest, slug: str) -> HttpResponse:
    device = get_object_or_404(
        Device.objects.select_related("owner"), slug=slug
    )
    return render(request, "devices/device_detail.html", {"device": device})
