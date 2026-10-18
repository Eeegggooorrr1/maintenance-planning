from unittest.mock import Mock, patch

from django.contrib.staticfiles import finders
from django.test import Client, SimpleTestCase, override_settings
from django.urls import resolve, reverse

import homepage.views as homepage_views
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
        pages = {
            "/": "homepage/index.html",
            "/devices/": "devices/device_list.html",
            "/tasks/": "maintenance_tasks/task_list.html",
        }
        for url, template_name in pages.items():
            response = self.client.get(url)
            assert response.status_code == 200
            assert "text/html" in response.headers["Content-Type"]
            assert b"bootstrap" in response.content.lower()
            self.assertTemplateUsed(response, template_name)
            self.assertTemplateUsed(response, "base.html")

    def test_views_no_longer_use_page_helper(self) -> None:
        assert not hasattr(homepage_views, "page")

    def test_device_pages_use_json_data(self) -> None:
        list_response = self.client.get("/devices/")
        detail_response = self.client.get("/devices/1/")

        assert list_response.status_code == 200
        assert "Всего устройств: 3" in list_response.content.decode()
        assert detail_response.status_code == 200
        assert "Стиральная машина" in detail_response.content.decode()
        self.assertTemplateUsed(
            detail_response,
            "devices/device_detail.html",
        )

    def test_task_pages_use_json_data(self) -> None:
        list_response = self.client.get("/tasks/")
        detail_response = self.client.get("/tasks/1/")

        assert list_response.status_code == 200
        assert "Всего задач: 2" in list_response.content.decode()
        assert detail_response.status_code == 200
        assert "Проверить фильтр" in detail_response.content.decode()
        self.assertTemplateUsed(
            detail_response,
            "maintenance_tasks/task_detail.html",
        )

    def test_empty_collections_are_handled_by_templates(self) -> None:
        repository = Mock()
        repository.list_all.return_value = []

        with patch(
            "devices.views.get_device_repository",
            return_value=repository,
        ):
            device_response = self.client.get("/devices/")
        with patch(
            "maintenance_tasks.views.get_task_repository",
            return_value=repository,
        ):
            task_response = self.client.get("/tasks/")

        assert "Устройства не найдены" in device_response.content.decode()
        assert "Задачи обслуживания не найдены" in (
            task_response.content.decode()
        )

    def test_static_files_are_discoverable(self) -> None:
        paths = (
            "homepage/css/style.css",
            "homepage/js/main.js",
            "homepage/img/logo.svg",
        )

        assert all(finders.find(path) for path in paths)

    def test_base_template_connects_static_assets(self) -> None:
        response = self.client.get("/")
        content = response.content.decode()

        assert "/static/homepage/css/style.css" in content
        assert "/static/homepage/js/main.js" in content
        assert "/static/homepage/img/logo.svg" in content
        assert 'id="current-year"' in content

    def test_missing_domain_objects_return_404(self) -> None:
        device_response = self.client.get("/devices/999/")
        task_response = self.client.get("/tasks/999/")

        assert device_response.status_code == 404
        assert task_response.status_code == 404
        self.assertTemplateUsed(
            device_response,
            "devices/device_detail.html",
        )
        self.assertTemplateUsed(
            task_response,
            "maintenance_tasks/task_detail.html",
        )

    def test_non_integer_identifiers_do_not_match_detail_routes(self) -> None:
        assert self.client.get("/devices/not-a-number/").status_code == 404
        assert self.client.get("/tasks/not-a-number/").status_code == 404

    @override_settings(DEBUG=False)
    def test_unknown_route_uses_custom_404_page(self) -> None:
        response = self.client.get("/unknown-page/")

        assert response.status_code == 404
        assert "страница не найдена" in response.content.decode()
