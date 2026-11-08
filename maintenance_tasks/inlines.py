from django.contrib import admin

from maintenance_tasks.models import Task


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    can_delete = False
    show_change_link = True
    fields = (
        "title",
        "device",
        "owner",
        "scheduled_date",
        "status",
        "priority",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).with_related()
