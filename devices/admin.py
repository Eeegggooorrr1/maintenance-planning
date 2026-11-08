from django.contrib import admin

from maintenance_tasks.inlines import TaskInline

from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "category",
        "brand",
        "service_interval_days",
        "next_service",
    )
    list_display_links = ("name",)
    list_editable = ("service_interval_days",)
    search_fields = ("name", "brand", "model", "serial_number", "owner__name")
    list_filter = ("category", "brand")
    list_select_related = ("owner",)
    autocomplete_fields = ("owner",)
    ordering = ("name", "pk")
    list_per_page = 20
    readonly_fields = ("slug", "next_service")
    inlines = (TaskInline,)

    @admin.display(description="Следующее обслуживание")
    def next_service(self, obj):
        return obj.next_service_date
