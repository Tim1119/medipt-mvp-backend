from rest_framework.permissions import BasePermission
from  apps.accounts.models import User
from rest_framework.exceptions import PermissionDenied
from shared.text_choices import UserRoles

class IsCaregiver(BasePermission):
    """Allows access only to patients for their own records."""

    message = "You do not have permission to access this data."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.role == UserRoles.PATIENT)

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.role == UserRoles.PATIENT