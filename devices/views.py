from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from maintenance_web.queries import find_device, list_devices


def devices(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "devices/device_list.html",
        {"devices": list_devices()},
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
