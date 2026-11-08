from django.db import migrations


def fill_slugs(apps, schema_editor):
    Device = apps.get_model("devices", "Device")
    for device in (
        Device.objects.using(schema_editor.connection.alias)
        .filter(slug__isnull=True)
        .iterator()
    ):
        device.slug = f"device-{device.pk}"
        device.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        (
            "devices",
            "0002_alter_device_options_device"
            "_slug_alter_device_brand_and_more",
        )
    ]
    operations = [migrations.RunPython(fill_slugs, migrations.RunPython.noop)]
