from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("devices/", include("devices.urls")),
    path("tasks/", include("maintenance_tasks.urls")),
]

handler404 = "homepage.views.page_not_found"
