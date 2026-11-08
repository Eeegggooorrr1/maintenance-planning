from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from db.import_json import import_data
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from devices.models import Device
from homepage.models import User
from maintenance_tasks.models import Task
from maintenance_web.queries import list_tasks, statistics


class ORMTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create(name="Иван", email="test@example.com")
        self.device = Device.objects.create(
            owner=self.owner, name="Чайник", category="Техника"
        )

    def test_crud_and_protected_relations(self):
        task = Task.objects.create(
            owner=self.owner,
            device=self.device,
            title="Очистка",
            scheduled_date=date(2026, 11, 5),
        )
        task.title = "Проверка"
        task.save()
        task.refresh_from_db()
        self.assertEqual(task.title, "Проверка")
        with self.assertRaises(ProtectedError):
            self.device.delete()
        task.delete()
        self.device.delete()
        self.assertFalse(Device.objects.exists())

    def test_validation_and_next_service_date(self):
        self.device.last_service_date = date(2026, 1, 1)
        self.device.service_interval_days = 30
        self.assertEqual(self.device.next_service_date, date(2026, 1, 31))
        other = User.objects.create(name="Другой", email="other@example.com")
        task = Task(
            owner=other,
            device=self.device,
            title="Тест",
            scheduled_date=date.today(),
        )
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_related_objects_load_in_one_query_and_zero_statistics(self):
        Task.objects.create(
            owner=self.owner,
            device=self.device,
            title="Тест",
            scheduled_date=date.today(),
        )
        with self.assertNumQueries(1):
            self.assertEqual(
                [(t.device.name, t.owner.name) for t in list_tasks()],
                [("Чайник", "Иван")],
            )
        empty = Device.objects.create(
            owner=self.owner, name="Пустое", category="Техника"
        )
        by_device, by_status = statistics()
        self.assertEqual(by_device.get(pk=empty.pk).task_count, 0)
        self.assertEqual(
            list(by_status), [{"status": "planned", "task_count": 1}]
        )

    def test_combined_filters_sorting_and_pagination(self):
        for i in range(8):
            Task.objects.create(
                owner=self.owner,
                device=self.device,
                title=f"Проверка {i}",
                scheduled_date=date(2026, 11, i + 1),
            )
        params = {
            "q": "Проверка",
            "device": self.device.pk,
            "status": "planned",
            "until": "2026-11-08",
            "sort": "-date",
        }
        response = self.client.get("/tasks/", params)
        self.assertEqual(response.context["page_obj"].paginator.count, 8)
        self.assertEqual(
            response.context["tasks"][0]["scheduled_date"], date(2026, 11, 8)
        )
        self.assertContains(response, "page=2")
        self.assertContains(response, "status=planned")
        params["page"] = 2
        response = self.client.get("/tasks/", params)
        self.assertEqual(len(response.context["tasks"]), 3)

    def test_invalid_parameters_and_page_boundaries(self):
        for params in (
            {"until": "bad"},
            {"device": "-1"},
            {"device": "9" * 5000},
            {"status": "bad"},
            {"sort": "bad"},
        ):
            response = self.client.get("/tasks/", params)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["errors"])
        for page in ("bad", "-1", "999"):
            self.assertEqual(
                self.client.get("/tasks/", {"page": page}).status_code, 200
            )
        self.assertEqual(self.client.get("/tasks/999/").status_code, 404)


class TransferTests(TestCase):
    def test_transfer_counts_links_and_repeat_protection(self):
        from django.conf import settings

        with TemporaryDirectory(dir=settings.BASE_DIR) as directory:
            source = Path(directory) / "source.sqlite"
            import_data(db_path=source)
            before = source.read_bytes()
            call_command("import_pr7", source=source)
            self.assertEqual(source.read_bytes(), before)
            self.assertTrue(User.objects.exists())
            self.assertEqual(
                Task.objects.get(pk=1).device.owner_id,
                Task.objects.get(pk=1).owner_id,
            )
            counts = (
                User.objects.count(),
                Device.objects.count(),
                Task.objects.count(),
            )
            with self.assertRaises(CommandError):
                call_command("import_pr7", source=source)
            self.assertEqual(
                counts,
                (
                    User.objects.count(),
                    Device.objects.count(),
                    Task.objects.count(),
                ),
            )
