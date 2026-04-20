from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import Invitation, Meeting, User

# Formulário de criação de funcionário, herda de UserCreationForm 
class EmployeeForm(UserCreationForm):
    first_name = forms.CharField(label="Nome", max_length=150)
    last_name = forms.CharField(label="Sobrenome", max_length=150)
    email = forms.EmailField(label="E-mail")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        labels = {"username": "Nome de usuário"}

    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        self.instance.role = User.EMPLOYEE
        self.instance.manager = manager

    def save(self, commit=True, manager=None):
        manager = manager or self.manager
        employee = super().save(commit=False)
        employee.role = User.EMPLOYEE
        employee.manager = manager
        if commit:
            employee.save()
        return employee

#Atualizar funcionário herda de ModelForm
class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username")
        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
            "username": "Nome de usuário",
        }

#Criar reunião herda de ModelForm
class MeetingForm(forms.ModelForm):
    invitees = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        label="Funcionários convidados",
        widget=forms.CheckboxSelectMultiple,
    )
    scheduled_for = forms.DateTimeField(
        label="Data e hora",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = Meeting
        fields = ("title", "description", "location", "scheduled_for")
        labels = {
            "title": "Título",
            "description": "Descrição",
            "location": "Local",
        }

    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        if manager:
            self.fields["invitees"].queryset = User.objects.filter(manager=manager, role=User.EMPLOYEE)
        if self.instance.pk:
            self.fields["invitees"].initial = self.instance.invitations.values_list("employee_id", flat=True)
            self.initial["scheduled_for"] = timezone.localtime(self.instance.scheduled_for).strftime("%Y-%m-%dT%H:%M")

    def clean_scheduled_for(self):
        scheduled_for = self.cleaned_data["scheduled_for"]
        if timezone.is_naive(scheduled_for):
            scheduled_for = timezone.make_aware(scheduled_for, timezone.get_current_timezone())
        return scheduled_for

    def save(self, commit=True):
        meeting = super().save(commit=False)
        meeting.created_by = self.manager
        if commit:
            meeting.save()
            self._save_invitations(meeting)
        return meeting

    def _save_invitations(self, meeting):
        selected_ids = set(self.cleaned_data["invitees"].values_list("id", flat=True))
        current_invitations = {inv.employee_id: inv for inv in meeting.invitations.all()}

        for employee_id, invitation in current_invitations.items():
            if employee_id not in selected_ids:
                invitation.delete()

        for employee in self.cleaned_data["invitees"]:
            Invitation.objects.get_or_create(meeting=meeting, employee=employee)

#Classe para padronizar a resposta do funcionário herda de ModelFOrm
class InvitationResponseForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ("status",)
        labels = {"status": "Sua resposta"}

    def save(self, commit=True):
        invitation = super().save(commit=False)
        invitation.responded_at = timezone.now()
        if commit:
            invitation.save()
        return invitation
