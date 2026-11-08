from devices.models import Device


def site_context(request) -> dict:
    return {"site_name": "ТехСервис", "device_count": Device.objects.count()}
