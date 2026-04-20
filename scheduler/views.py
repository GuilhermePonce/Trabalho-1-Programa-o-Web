from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmployeeForm, EmployeeUpdateForm, InvitationResponseForm, MeetingForm
from .models import Invitation, Meeting, User


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def _acting_user(request):
    user = request.user
    preview_user = None
    preview_id = request.GET.get("as_user")
    if user.is_superuser and preview_id:
        preview_user = get_object_or_404(User, pk=preview_id)
        return preview_user, preview_user
    return user, preview_user


def _can_manage(user):
    return user.is_superuser or user.role == User.MANAGER


def _manager_or_403(user):
    if not _can_manage(user):
        raise Http404("Área disponível apenas para gerentes.")


@login_required
def dashboard(request):
    acting_user, preview_user = _acting_user(request)
    context = {"acting_user": acting_user, "preview_user": preview_user}

    if _can_manage(acting_user):
        employees = User.objects.filter(manager=acting_user, role=User.EMPLOYEE)
        meetings = Meeting.objects.filter(created_by=acting_user).annotate(
            accepted_count=Count("invitations", filter=Q(invitations__status=Invitation.ACCEPTED)),
            pending_count=Count("invitations", filter=Q(invitations__status=Invitation.PENDING)),
        )
        context.update(
            {
                "employees": employees[:5],
                "employees_count": employees.count(),
                "meetings": meetings[:5],
                "meetings_count": meetings.count(),
                "pending_responses": Invitation.objects.filter(
                    meeting__created_by=acting_user,
                    status=Invitation.PENDING,
                ).count(),
                "all_members": User.objects.exclude(pk=request.user.pk).order_by("role", "first_name", "username")
                if request.user.is_superuser
                else User.objects.none(),
            }
        )
        return render(request, "scheduler/dashboard_manager.html", context)

    invitations = Invitation.objects.filter(employee=acting_user).select_related("meeting", "meeting__created_by")
    context.update(
        {
            "invitations": invitations[:6],
            "pending_invitations": invitations.filter(status=Invitation.PENDING).count(),
            "accepted_invitations": invitations.filter(status=Invitation.ACCEPTED).count(),
        }
    )
    return render(request, "scheduler/dashboard_employee.html", context)


@login_required
def employee_list(request):
    acting_user, preview_user = _acting_user(request)
    _manager_or_403(acting_user)
    employees = User.objects.filter(manager=acting_user, role=User.EMPLOYEE).order_by("first_name", "username")
    return render(
        request,
        "scheduler/employee_list.html",
        {"employees": employees, "acting_user": acting_user, "preview_user": preview_user},
    )


@login_required
def employee_create(request):
    acting_user, preview_user = _acting_user(request)
    _manager_or_403(acting_user)
    if request.method == "POST":
        form = EmployeeForm(request.POST, manager=acting_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Funcionário cadastrado com sucesso.")
            return redirect("employee_list")
    else:
        form = EmployeeForm(manager=acting_user)
    return render(
        request,
        "scheduler/employee_form.html",
        {"form": form, "page_title": "Novo funcionário", "acting_user": acting_user, "preview_user": preview_user},
    )


@login_required
def employee_update(request, user_id):
    acting_user, preview_user = _acting_user(request)
    _manager_or_403(acting_user)
    employee = get_object_or_404(User, pk=user_id, manager=acting_user, role=User.EMPLOYEE)
    if request.method == "POST":
        form = EmployeeUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            updated_employee = form.save(commit=False)
            updated_employee.role = User.EMPLOYEE
            updated_employee.manager = acting_user
            updated_employee.save()
            messages.success(request, "Funcionário atualizado com sucesso.")
            return redirect("employee_list")
    else:
        form = EmployeeUpdateForm(instance=employee)
    return render(
        request,
        "scheduler/employee_form.html",
        {
            "form": form,
            "page_title": f"Editar {employee}",
            "employee": employee,
            "acting_user": acting_user,
            "preview_user": preview_user,
        },
    )


@login_required
def employee_delete(request, user_id):
    acting_user, preview_user = _acting_user(request)
    _manager_or_403(acting_user)
    employee = get_object_or_404(User, pk=user_id, manager=acting_user, role=User.EMPLOYEE)
    if request.method == "POST":
        employee.delete()
        messages.success(request, "Funcionário removido com sucesso.")
        return redirect("employee_list")
    return render(
        request,
        "scheduler/confirm_delete.html",
        {
            "object_name": employee,
            "entity_name": "funcionário",
            "acting_user": acting_user,
            "preview_user": preview_user,
        },
    )


@login_required
def meeting_list(request):
    acting_user, preview_user = _acting_user(request)
    _manager_or_403(acting_user)
    meetings = Meeting.objects.filter(created_by=acting_user).prefetch_related("invitations__employee")
    return render(
        request,
        "scheduler/meeting_list.html",
        {"meetings": meetings, "acting_user": acting_user, "preview_user": preview_user},
    )


@login_required
def meeting_create(request):
    acting_user, preview_user = _acting_user(request)
    _manager_or_403(acting_user)
    if request.method == "POST":
        form = MeetingForm(request.POST, manager=acting_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Reunião criada com sucesso.")
            return redirect("meeting_list")
    else:
        form = MeetingForm(manager=acting_user)
    return render(
        request,
        "scheduler/meeting_form.html",
        {"form": form, "page_title": "Nova reunião", "acting_user": acting_user, "preview_user": preview_user},
    )


@login_required
def meeting_update(request, meeting_id):
    acting_user, preview_user = _acting_user(request)
    _manager_or_403(acting_user)
    meeting = get_object_or_404(Meeting, pk=meeting_id, created_by=acting_user)
    if request.method == "POST":
        form = MeetingForm(request.POST, instance=meeting, manager=acting_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Reunião atualizada com sucesso.")
            return redirect("meeting_detail", meeting_id=meeting.id)
    else:
        form = MeetingForm(instance=meeting, manager=acting_user)
    return render(
        request,
        "scheduler/meeting_form.html",
        {
            "form": form,
            "page_title": f"Editar reunião: {meeting.title}",
            "meeting": meeting,
            "acting_user": acting_user,
            "preview_user": preview_user,
        },
    )


@login_required
def meeting_delete(request, meeting_id):
    acting_user, preview_user = _acting_user(request)
    _manager_or_403(acting_user)
    meeting = get_object_or_404(Meeting, pk=meeting_id, created_by=acting_user)
    if request.method == "POST":
        meeting.delete()
        messages.success(request, "Reunião excluída com sucesso.")
        return redirect("meeting_list")
    return render(
        request,
        "scheduler/confirm_delete.html",
        {
            "object_name": meeting,
            "entity_name": "reunião",
            "acting_user": acting_user,
            "preview_user": preview_user,
        },
    )


@login_required
def meeting_detail(request, meeting_id):
    acting_user, preview_user = _acting_user(request)
    meeting = get_object_or_404(Meeting.objects.prefetch_related("invitations__employee"), pk=meeting_id)
    if _can_manage(acting_user):
        if meeting.created_by_id != acting_user.id:
            raise Http404("Reunião não encontrada.")
        return render(
            request,
            "scheduler/meeting_detail.html",
            {"meeting": meeting, "acting_user": acting_user, "preview_user": preview_user},
        )

    invitation = get_object_or_404(Invitation, meeting=meeting, employee=acting_user)
    return redirect("invitation_detail", invitation_id=invitation.id)


@login_required
def invitation_list(request):
    acting_user, preview_user = _acting_user(request)
    if _can_manage(acting_user):
        return HttpResponseForbidden("Gerentes devem acessar a área de reuniões.")
    invitations = Invitation.objects.filter(employee=acting_user).select_related("meeting", "meeting__created_by")
    return render(
        request,
        "scheduler/invitation_list.html",
        {"invitations": invitations, "acting_user": acting_user, "preview_user": preview_user},
    )


@login_required
def invitation_detail(request, invitation_id):
    acting_user, preview_user = _acting_user(request)
    if _can_manage(acting_user):
        return HttpResponseForbidden("Gerentes não respondem convites.")
    invitation = get_object_or_404(
        Invitation.objects.select_related("meeting", "meeting__created_by"),
        pk=invitation_id,
        employee=acting_user,
    )
    if request.method == "POST":
        form = InvitationResponseForm(request.POST, instance=invitation)
        if form.is_valid():
            form.save()
            messages.success(request, "Sua resposta foi registrada.")
            return redirect("invitation_list")
    else:
        form = InvitationResponseForm(instance=invitation)
    return render(
        request,
        "scheduler/invitation_detail.html",
        {"invitation": invitation, "form": form, "acting_user": acting_user, "preview_user": preview_user},
    )
