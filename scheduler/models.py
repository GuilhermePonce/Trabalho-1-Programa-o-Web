from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

#Classe usuário genérica que baseia qualquer usuário
class User(AbstractUser):
    MANAGER = "manager"
    EMPLOYEE = "employee"
    ROLE_CHOICES = [
        (MANAGER, "Gerente"),
        (EMPLOYEE, "Funcionário"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=EMPLOYEE)
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members",
        limit_choices_to={"role": MANAGER},
    )

    def clean(self):
        super().clean()
        if self.role == self.MANAGER:
            self.manager = None
        if self.role == self.EMPLOYEE and not self.manager and not self.is_superuser:
            raise ValidationError("Funcionários precisam estar vinculados a um gerente.")

    @property
    def role_label(self):
        if self.is_superuser:
            return "Administrador"
        return dict(self.ROLE_CHOICES).get(self.role, "Usuário")

    def __str__(self):
        return self.get_full_name() or self.username

#Classe reunião que descreve as reuniões
class Meeting(models.Model):
    title = models.CharField("Título", max_length=120)
    description = models.TextField("Descrição")
    location = models.CharField("Local", max_length=120)
    scheduled_for = models.DateTimeField("Data e hora")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_meetings",
        limit_choices_to={"role": User.MANAGER},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_for", "title"]

    def clean(self):
        super().clean()
        if self.created_by_id and self.created_by.role != User.MANAGER and not self.created_by.is_superuser:
            raise ValidationError("Apenas gerentes podem criar reuniões.")

    @property
    def is_past(self):
        return self.scheduled_for < timezone.now()

    def __str__(self):
        return self.title

#Classe convite que descreve os convites para as reuniões
class Invitation(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    STATUS_CHOICES = [
        (PENDING, "Pendente"),
        (ACCEPTED, "Aceita"),
        (DECLINED, "Recusada"),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="invitations")
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="invitations",
        limit_choices_to={"role": User.EMPLOYEE},
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("meeting", "employee")
        ordering = ["employee__first_name", "employee__username"]

    def clean(self):
        super().clean()
        if self.employee.role != User.EMPLOYEE and not self.employee.is_superuser:
            raise ValidationError("Convites só podem ser enviados para funcionários.")
        if (
            self.meeting_id
            and self.employee_id
            and self.meeting.created_by_id
            and self.employee.manager_id != self.meeting.created_by_id
        ):
            raise ValidationError("O funcionário convidado precisa pertencer ao gerente da reunião.")

    def __str__(self):
        return f"{self.employee} - {self.meeting}"
