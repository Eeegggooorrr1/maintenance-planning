from django.urls import path

from . import views

app_name = "maintenance_tasks"

urlpatterns = [
    path("", views.tasks, name="list"),
    path("<int:task_id>/", views.task_detail, name="detail"),
]
