from django.test import Client, SimpleTestCase, override_settings
from django.urls import resolve, reverse

from devices.views import device_detail, devices
from homepage.views import index
from maintenance_tasks.views import task_detail, tasks


class RoutingTests(SimpleTestCase):
    def test_named_routes_are_reversible(self) -> None:
        assert reverse("homepage:index") == "/"
        assert reverse("devices:list") == "/devices/"
        assert reverse("devices:detail", args=[1]) == "/devices/1/"
        assert reverse("maintenance_tasks:list") == "/tasks/"
        assert reverse("maintenance_tasks:detail", args=[1]) == "/tasks/1/"

    def test_routes_resolve_to_expected_views(self) -> None:
        assert resolve("/").func is index
        assert resolve("/devices/").func is devices
        assert resolve("/devices/1/").func is device_detail
        assert resolve("/tasks/").func is tasks
        assert resolve("/tasks/1/").func is task_detail


class PageTests(SimpleTestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_main_pages_return_html(self) -> None:
        for url in ("/", "/devices/", "/tasks/"):
            response = self.client.get(url)
            assert response.status_code == 200
            assert "text/html" in response.headers["Content-Type"]
            assert b"bootstrap" in response.content.lower()

    def test_device_pages_use_json_data(self) -> None:
        response = self.client.get("/devices/1/")

        assert response.status_code == 200
        assert "Стиральная машина" in response.content.decode()

    def test_task_pages_use_json_data(self) -> None:
        response = self.client.get("/tasks/1/")

        assert response.status_code == 200
        assert "Проверить фильтр" in response.content.decode()

    def test_missing_domain_objects_return_404(self) -> None:
        assert self.client.get("/devices/999/").status_code == 404
        assert self.client.get("/tasks/999/").status_code == 404

    def test_non_integer_identifiers_do_not_match_detail_routes(self) -> None:
        assert self.client.get("/devices/not-a-number/").status_code == 404
        assert self.client.get("/tasks/not-a-number/").status_code == 404

    @override_settings(DEBUG=False)
    def test_unknown_route_uses_custom_404_page(self) -> None:
        response = self.client.get("/unknown-page/")

        assert response.status_code == 404
        assert "страница не найдена" in response.content.decode()
