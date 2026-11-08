from django.urls import path

from . import views

app_name = "devices"

urlpatterns = [
    path("", views.devices, name="list"),
    path("<int:device_id>/", views.device_detail, name="detail"),
    path("<slug:slug>/", views.device_by_slug, name="detail_slug"),
]
