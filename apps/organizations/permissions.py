from rest_framework.permissions import BasePermission
from shared.text_choices import UserRoles
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission



class IsOrganizationWithAccount(BasePermission):
    """
    Allows access only to users with the organization role
    and ensures they have an associated organization object.
    """
    message = "You do not have permission to access this data."

    def has_permission(self, request, view):
        # Must be authenticated (you already have IsAuthenticated)
        user = request.user
        if not user or user.role != UserRoles.ORGANIZATION:
            return False

        # Ensure user has an organization
        if not hasattr(user, "organization") or user.organization is None:
            raise NotFound("Organization not found for this user.")

        return True

    def has_object_permission(self, request, view, obj):
        # Optional: enforce object-level check if needed
        return getattr(request.user, "organization", None) == obj


class IsOrganization(BasePermission):
    """
    Allows access only to users with the organization role.
    """
    message = "You do not have permission to access this data."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == UserRoles.ORGANIZATION)

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.role == UserRoles.ORGANIZATION
