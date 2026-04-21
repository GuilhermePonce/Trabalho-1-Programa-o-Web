from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from scheduler.models import Invitation, Meeting, User


class Command(BaseCommand):
    help = "Cria usuários e reuniões de demonstração."

    def handle(self, *args, **options):
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Admin",
                "last_name": "Teste",
                "email": "admin@example.com",
                "role": User.MANAGER,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("admin12345")
            admin_user.save()

        manager, created = User.objects.get_or_create(
            username="gerente_demo",
            defaults={
                "first_name": "Marina",
                "last_name": "Costa",
                "email": "gerente@example.com",
                "role": User.MANAGER,
            },
        )
        if created:
            manager.set_password("gerente12345")
            manager.save()

        employee_one, created = User.objects.get_or_create(
            username="funcionario_demo1",
            defaults={
                "first_name": "Carlos",
                "last_name": "Lima",
                "email": "carlos@example.com",
                "role": User.EMPLOYEE,
                "manager": manager,
            },
        )
        if created:
            employee_one.set_password("func12345")
            employee_one.save()

        employee_two, created = User.objects.get_or_create(
            username="funcionario_demo2",
            defaults={
                "first_name": "Ana",
                "last_name": "Souza",
                "email": "ana@example.com",
                "role": User.EMPLOYEE,
                "manager": manager,
            },
        )
        if created:
            employee_two.set_password("func12345")
            employee_two.save()

        meeting, _ = Meeting.objects.get_or_create(
            title="Reunião de alinhamento",
            created_by=manager,
            defaults={
                "description": "Revisar pendências e próximos passos do time.",
                "location": "Sala principal",
                "scheduled_for": timezone.now() + timedelta(days=2),
            },
        )
        Invitation.objects.get_or_create(meeting=meeting, employee=employee_one)
        Invitation.objects.get_or_create(meeting=meeting, employee=employee_two)

        self.stdout.write(self.style.SUCCESS("Dados de demonstração criados/atualizados com sucesso."))
