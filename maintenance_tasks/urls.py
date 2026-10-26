from django.urls import path

from . import views

app_name = "maintenance_tasks"

urlpatterns = [
    path("", views.tasks, name="list"),
    path("due/", views.due_search, name="due"),
    path("statistics/", views.task_statistics, name="statistics"),
    path("<int:task_id>/", views.task_detail, name="detail"),
]
