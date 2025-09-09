from rest_framework.exceptions import NotFound

class OrganizationContextMixin:
    """
    Provides a `get_organization` method for views
    """
    def get_organization(self):
        user = self.request.user

        if hasattr(user, "organization") and user.organization:
            return user.organization

        if hasattr(user, "caregiver") and user.caregiver.organization:
            return user.caregiver.organization
        
        if hasattr(user, "patient") and user.patient.organization:
            return user.patient.organization

        raise NotFound("Organization not found for this user.")
