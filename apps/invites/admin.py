from django.contrib import admin
from .models import Organization

from django.contrib import admin
from .models import CaregiverInvite, InvitationStatus


@admin.register(CaregiverInvite)
class CaregiverInviteAdmin(admin.ModelAdmin):
    list_display = ("email","organization","role","status","invited_by","resend_count","expires_at","created_at")
    list_filter = ("status","role","organization","invited_by",
        "created_at",
        "expires_at",
    )
    search_fields = ("email", "organization__name", "invited_by__email")
    readonly_fields = ("token", "created_at", "updated_at", "resend_count")
    ordering = ("-created_at",)
    fieldsets = (
        ("Invite Info", {
            "fields": ("email", "organization", "role", "status", "token")
        }),
        ("Sender Info", {
            "fields": ("invited_by", "resend_count")
        }),
        ("Timestamps", {
            "fields": ("expires_at", "created_at", "updated_at")
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """Optionally prevent deleting expired invites."""
        if obj and obj.status == InvitationStatus.ACCEPTED:
            return False
        return super().has_delete_permission(request, obj)
