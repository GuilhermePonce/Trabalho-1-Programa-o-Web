from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Invitation, Meeting, User


class SchedulerFlowTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="gerente",
            password="SenhaForte123",
            first_name="Paula",
            role=User.MANAGER,
        )
        self.employee = User.objects.create_user(
            username="funcionario",
            password="SenhaForte123",
            first_name="Bruno",
            role=User.EMPLOYEE,
            manager=self.manager,
        )
        self.meeting = Meeting.objects.create(
            title="Planejamento semanal",
            description="Alinhar prioridades",
            location="Sala 2",
            scheduled_for=timezone.now() + timedelta(days=1),
            created_by=self.manager,
        )
        self.invitation = Invitation.objects.create(meeting=self.meeting, employee=self.employee)

    def test_manager_dashboard_loads(self):
        self.client.login(username="gerente", password="SenhaForte123")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Painel do gerente")
        self.assertContains(response, "Planejamento semanal")

    def test_employee_can_answer_invitation(self):
        self.client.login(username="funcionario", password="SenhaForte123")
        response = self.client.post(reverse("invitation_detail", args=[self.invitation.id]), {"status": Invitation.ACCEPTED})
        self.assertRedirects(response, reverse("invitation_list"))
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.ACCEPTED)
        self.assertIsNotNone(self.invitation.responded_at)

    def test_manager_can_create_employee(self):
        self.client.login(username="gerente", password="SenhaForte123")
        response = self.client.post(
            reverse("employee_create"),
            {
                "username": "novo_funcionario",
                "first_name": "Lia",
                "last_name": "Silva",
                "email": "lia@example.com",
                "password1": "PlanoSeguro321!",
                "password2": "PlanoSeguro321!",
            },
        )
        self.assertRedirects(response, reverse("employee_list"))
        self.assertTrue(User.objects.filter(username="novo_funcionario", manager=self.manager).exists())
