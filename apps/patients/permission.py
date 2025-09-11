from rest_framework.permissions import BasePermission

from shared.text_choices import UserRoles

class IsPatientSelf(BasePermission):
    """
    Only allow a patient to update their own record.
    """
    def has_object_permission(self, request, view, obj):
        # Only patients can update their own info
        if request.method in ("PUT", "PATCH"):
            return obj.user == request.user
        return True
    

class IsPatient(BasePermission):
    """
    Allows access only to users with the organization role.
    """
    message = "You do not have permission to access this data."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.role == UserRoles.PATIENT)

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.role == UserRoles.PATIENT
