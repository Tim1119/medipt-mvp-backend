from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRoles(models.TextChoices):
    """User role choices with centralized permission management"""

    ORGANIZATION = "ORGANIZATION", _("Organization")
    CAREGIVER = "CAREGIVER", _("Caregiver")
    PATIENT = "PATIENT", _("Patient")

    @classmethod
    def get_role_permissions(cls, role):
        """Centralized permission logic for each role"""
        permissions = {
            cls.ORGANIZATION: {
                "can_invite_caregivers": True,
                "can_manage_caregivers": True,
                "can_register_patients": True,
                "can_manage_patients": True,
                "can_view_all_patient_data": True,
                "can_view_all_diagnoses": True,
                "can_export_data": True,
                "can_view_analytics": True,
                "can_manage_organization_settings": True,
                "can_view_audit_logs": True,
                "can_deactivate_users": True,
            },
            cls.CAREGIVER: {
                "can_view_assigned_patients": True,
                "can_create_diagnoses": True,
                "can_edit_patient_records": True,
                "can_view_medical_history": True,
                "can_schedule_appointments": True,
                "can_search_patients": True,
                "can_edit_own_profile": True,
                "can_view_own_schedule": True,
            },
            cls.PATIENT: {
                "can_view_own_profile": True,
                "can_edit_own_basic_info": True,
                "can_view_own_medical_records": True,
                "can_view_own_diagnoses": True,
                "can_view_own_appointments": True,
                "can_request_appointment": True,
                "can_message_caregivers": True,
                "can_download_own_records": True,
            },
        }
        return permissions.get(role, {})
