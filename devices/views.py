from html import escape

from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from homepage.views import page
from maintenance_web.repositories import get_device_repository


def devices(request: HttpRequest) -> HttpResponse:
    items = "".join(
        (
            '<a class="list-group-item list-group-item-action" '
            f'href="{reverse("devices:detail", args=[device.id])}">'
            f"{escape(device.name)} - {escape(device.category)}"
            "</a>"
        )
        for device in get_device_repository().list_all()
    )
    content = f"""
    <h1>Устройства</h1>
    <div class="list-group">{items}</div>
    """
    return HttpResponse(page("ТехСервис - устройства", content))


def device_detail(
    request: HttpRequest,
    device_id: int,
) -> HttpResponse:
    list_url = reverse("devices:list")
    device = get_device_repository().find_by_id(device_id)
    if device is None:
        content = f"""
        <h1 class="text-danger">Устройство не найдено</h1>
        <a href="{list_url}" class="btn btn-outline-secondary">
            К списку устройств
        </a>
        """
        return HttpResponse(
            page("Устройство не найдено", content),
            status=404,
        )

    next_service = device.next_service_date or "не запланировано"
    brand = escape(device.brand) or "не указан"
    model = escape(device.model) or "не указана"
    content = f"""
    <div class="card">
        <div class="card-body">
            <h1 class="card-title">{escape(device.name)}</h1>
            <p><strong>ID:</strong> {device.id}</p>
            <p><strong>Категория:</strong> {escape(device.category)}</p>
            <p><strong>Бренд:</strong> {brand}</p>
            <p><strong>Модель:</strong> {model}</p>
            <p><strong>Следующее обслуживание:</strong> {next_service}</p>
            <a href="{list_url}" class="btn btn-outline-secondary">
                К списку устройств
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(device.name, content))
