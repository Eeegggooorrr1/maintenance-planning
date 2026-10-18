from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from maintenance_web.repositories import get_device_repository


def devices(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "devices/device_list.html",
        {"devices": get_device_repository().list_all()},
    )


def device_detail(
    request: HttpRequest,
    device_id: int,
) -> HttpResponse:
    device = get_device_repository().find_by_id(device_id)
    return render(
        request,
        "devices/device_detail.html",
        {"device": device},
        status=404 if device is None else 200,
    )
