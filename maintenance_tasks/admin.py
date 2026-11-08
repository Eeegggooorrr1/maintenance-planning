from django.contrib import admin, messages

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "device",
        "owner",
        "scheduled_date",
        "priority",
        "status",
    )
    list_display_links = ("title",)
    search_fields = ("title", "device__name", "owner__name", "owner__email")
    list_filter = ("status", "priority", "scheduled_date")
    list_select_related = ("device", "owner")
    autocomplete_fields = ("device", "owner")
    ordering = ("scheduled_date", "pk")
    date_hierarchy = "scheduled_date"
    list_per_page = 20
    readonly_fields = ("completed_at",)
    actions = ("cancel_tasks", "restore_tasks")

    @admin.action(
        permissions=["change"],
        description="Отменить выбранные незавершённые задачи",
    )
    def cancel_tasks(self, request, queryset):
        count = queryset.active().update(status=Task.Status.CANCELLED)
        self.message_user(
            request, f"Отменено задач: {count}", messages.SUCCESS
        )

    @admin.action(
        permissions=["change"], description="Вернуть отменённые задачи в план"
    )
    def restore_tasks(self, request, queryset):
        count = queryset.cancelled().update(status=Task.Status.PLANNED)
        self.message_user(
            request, f"Возвращено в план: {count}", messages.SUCCESS
        )
