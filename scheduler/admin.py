from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Invitation, Meeting, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Perfil", {"fields": ("role", "manager")}),
    )
    list_display = ("username", "first_name", "last_name", "role", "manager", "is_superuser")
    list_filter = ("role", "is_superuser", "is_staff")


class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 1


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("title", "scheduled_for", "location", "created_by")
    inlines = [InvitationInline]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("meeting", "employee", "status", "responded_at")
    list_filter = ("status",)
