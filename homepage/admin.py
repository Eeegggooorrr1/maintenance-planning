from django.contrib import admin

from maintenance_tasks.inlines import TaskInline

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "role")
    list_display_links = ("name",)
    search_fields = ("name", "email")
    list_filter = ("role",)
    ordering = ("name", "pk")
    list_per_page = 20
    inlines = (TaskInline,)


admin.site.site_header = "ТехСервис — управление обслуживанием"
admin.site.site_title = "ТехСервис"
admin.site.index_title = "Данные проекта"
