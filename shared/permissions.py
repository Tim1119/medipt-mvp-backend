from functools import wraps
from typing import List

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class RoleBasedPermission(BasePermission):
    """Base permission class for role-based access"""

    allowed_roles: List[str] = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not self.allowed_roles:
            return True

        return request.user.role in self.allowed_roles

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


# Permission decorators
def require_permission(permission_name):
    """Decorator to require specific permission for views"""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")

            if not request.user.has_permission(permission_name):
                raise PermissionDenied(f"Permission '{permission_name}' required")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def require_role(required_role):
    """Decorator to require specific role"""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role != required_role:
                raise PermissionDenied(f"Role '{required_role}' required")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
