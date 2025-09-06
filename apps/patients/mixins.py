import logging
from django.contrib.auth import get_user_model
from django.core.validators import validate_email as  RegexValidator
from rest_framework import serializers

logger = logging.getLogger(__name__)
User = get_user_model()


from django.core.validators import RegexValidator
from rest_framework import serializers

class ValidationMixin:
    """Common validation methods for patient-related serializers."""

    @staticmethod
    def validate_name_field(value, field_name):
        """Validate name fields (first_name, last_name)."""
        if value:
            validator = RegexValidator(
                r'^[a-zA-Z\s-]+$',
                message=f"{field_name} can only contain letters, spaces, or hyphens."
            )
            validator(value)
        return value

    @staticmethod
    def validate_phone_number(value):
        """Validate phone number format."""
        if value:
            validator = RegexValidator(
                r'^\+?1?\d{9,15}$',
                message="Phone number must be a valid format (e.g., +1234567890)."
            )
            validator(value)
        return value

    @staticmethod
    def validate_profile_picture(value):
        """Validate profile picture format only if possible."""
        if value:
            # For CloudinaryResource, skip name/size check
            try:
                filename = value.name
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    raise serializers.ValidationError(
                        "Profile picture must be a JPG or PNG file."
                    )
            except AttributeError:
                # CloudinaryResource has no .name, so skip this check
                pass
        return value

from rest_framework import serializers
from .models import PatientMedicalRecord 

class PatientRepresentationMixin:
    """
    Mixin to add common user-related fields to patient serializers.
    """
    def add_user_fields_to_representation(self, instance, representation):
        representation['email'] = instance.user.email
        representation['role'] = instance.user.role
        representation['active'] = instance.user.is_active
        representation['verified'] = instance.user.is_verified
        return representation

    def add_medical_record_to_representation(self, instance, representation):
        from .serializers import PatientMedicalRecordSerializer
        try:
            medical_record = instance.patientmedicalrecord
            representation['medical_record'] = PatientMedicalRecordSerializer(medical_record).data
        except PatientMedicalRecord.DoesNotExist:
            representation['medical_record'] = {}
        return representation