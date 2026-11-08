from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from devices.models import Device
from homepage.models import User
from maintenance_tasks.models import Task
from maintenance_web.queries import devices_without_tasks_on, task_totals


class AdminAndQueryTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create(name="Иван", email="ivan@example.com")
        self.device = Device.objects.create(
            owner=self.owner, name="Чайник", category="Кухня"
        )
        self.task = Task.objects.create(
            owner=self.owner,
            device=self.device,
            title="Очистить",
            scheduled_date=date(2026, 11, 5),
        )
        self.admin = get_user_model().objects.create_superuser(
            username="testadmin", password="test-password-123"
        )

    def test_admin_requires_staff_and_permissions(self):
        url = reverse("admin:maintenance_tasks_task_changelist")
        self.assertEqual(self.client.get(url).status_code, 302)
        staff = get_user_model().objects.create_user(
            username="staff", is_staff=True
        )
        self.client.force_login(staff)
        self.assertEqual(self.client.get(url).status_code, 403)
        staff.user_permissions.add(
            Permission.objects.get(codename="view_task")
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="action"')
        self.client.post(url, {
            "action": "cancel_tasks", "_selected_action": [self.task.pk],
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.PLANNED)

    def test_admin_lists_search_and_related_inlines(self):
        self.client.force_login(self.admin)
        for name in (
            "homepage_user",
            "devices_device",
            "maintenance_tasks_task",
        ):
            self.assertEqual(
                self.client.get(
                    reverse(f"admin:{name}_changelist")
                ).status_code,
                200,
            )
        response = self.client.get(
            reverse("admin:maintenance_tasks_task_changelist"),
            {"q": "Чайник", "status__exact": "planned"},
        )
        self.assertContains(response, "Очистить")
        for name, pk in (
            ("devices_device", self.device.pk),
            ("homepage_user", self.owner.pk),
        ):
            response = self.client.get(
                reverse(f"admin:{name}_change", args=[pk])
            )
            self.assertContains(response, "Очистить")
            self.assertContains(response, "tasks-group")

    def test_admin_actions_respect_terminal_statuses(self):
        completed = Task.objects.create(
            owner=self.owner,
            device=self.device,
            title="Завершено",
            scheduled_date=date.today(),
            status=Task.Status.COMPLETED,
        )
        self.client.force_login(self.admin)
        url = reverse("admin:maintenance_tasks_task_changelist")
        self.client.post(
            url,
            {
                "action": "cancel_tasks",
                "_selected_action": [self.task.pk, completed.pk],
            },
        )
        self.task.refresh_from_db()
        completed.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.CANCELLED)
        self.assertEqual(completed.status, Task.Status.COMPLETED)
        self.client.post(
            url,
            {
                "action": "restore_tasks",
                "_selected_action": [self.task.pk, completed.pk],
            },
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.PLANNED)

    def test_admin_form_rejects_wrong_owner(self):
        other = User.objects.create(name="Другой", email="other@example.com")
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("admin:maintenance_tasks_task_add"),
            {
                "owner": other.pk,
                "device": self.device.pk,
                "title": "Ошибка",
                "scheduled_date": "2026-11-05",
                "priority": 2,
                "status": "planned",
                "_save": "Сохранить",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Владелец задачи должен совпадать")
        self.assertEqual(Task.objects.count(), 1)

    def test_queryset_availability_and_totals(self):
        self.assertEqual(
            Task.objects.active().for_date(date(2026, 11, 5)).count(), 1
        )
        self.assertFalse(
            devices_without_tasks_on(date(2026, 11, 5))
            .filter(pk=self.device.pk)
            .exists()
        )
        self.task.status = Task.Status.CANCELLED
        self.task.save()
        self.assertTrue(
            devices_without_tasks_on(date(2026, 11, 5))
            .filter(pk=self.device.pk)
            .exists()
        )
        self.assertEqual(Task.objects.cancelled().count(), 1)
        self.assertEqual(
            task_totals(),
            {"total": 1, "active": 0, "cancelled": 1, "completed": 0},
        )
        self.task.status = Task.Status.COMPLETED
        self.task.save()
        self.assertEqual(Task.objects.completed().count(), 1)
        self.assertTrue(devices_without_tasks_on(date(2026, 11, 5)).exists())

    def test_slug_url_context_and_computed_value(self):
        self.assertTrue(self.device.slug.isascii())
        original_slug = self.device.slug
        self.device.name = "Новое название"
        self.device.last_service_date = date(2026, 11, 1)
        self.device.service_interval_days = 10
        self.device.save()
        self.device.refresh_from_db()
        self.assertEqual(self.device.next_service_date, date(2026, 11, 11))
        self.assertEqual(self.device.slug, original_slug)
        for url in (self.device.get_absolute_url(), "/", "/tasks/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["site_name"], "ТехСервис")
            self.assertEqual(response.context["device_count"], 1)
        self.assertEqual(
            self.client.get("/devices/unknown-slug/").status_code, 404
        )

    def test_list_query_count_is_constant_and_owner_filter_works(self):
        for index in range(6):
            Task.objects.create(
                owner=self.owner,
                device=self.device,
                title=f"Задача {index}",
                scheduled_date=date.today(),
            )
        with self.assertNumQueries(5):
            response = self.client.get("/tasks/", {"owner": self.owner.pk})
        self.assertEqual(len(response.context["tasks"]), 5)
        self.assertContains(response, "Чайник")
        self.assertEqual(
            self.client.get("/tasks/?owner=bad")
            .context["page_obj"]
            .paginator.count,
            0,
        )
        self.assertContains(
            self.client.get("/devices/?available_on=bad"),
            "Укажите корректную дату",
        )
