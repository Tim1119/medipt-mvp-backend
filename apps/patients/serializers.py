import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email as django_validate_email, RegexValidator
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shared.text_choices import UserRoles
from .mixins import ValidationMixin
from apps.caregivers.models import Caregiver
# from apps.accounts.user_roles import UserRoles
# from .exceptions import PatientNotificationFailedException
from .mixins import PatientRepresentationMixin
from .models import Patient, PatientMedicalRecord, PatientDiagnosisDetails, VitalSign
from .patient_service import PatientService,PatientDiagnosisVitalSignService
from rest_framework import viewsets, status

logger = logging.getLogger(__name__)
User = get_user_model()




class PatientMedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer for patient medical records."""
    
    class Meta:
        model = PatientMedicalRecord
        fields = ['blood_group', 'genotype', 'weight', 'height', 'allergies']


class BasePatientSerializer(ValidationMixin, serializers.ModelSerializer):
    """Base serializer for patient with common fields and validations."""
    
    medical_record = PatientMedicalRecordSerializer(required=False)

    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'medical_id', 'date_of_birth', 
            'marital_status', 'profile_picture', 'gender', 'phone_number', 
            'emergency_phone_number', 'address', 'medical_record'
        ]
        read_only_fields = ['id', 'medical_id']

    def validate_first_name(self, value):
        return self.validate_name_field(value, "First name")

    def validate_last_name(self, value):
        return self.validate_name_field(value, "Last name")


class PatientSerializer(PatientRepresentationMixin, serializers.ModelSerializer):
    """Simple patient serializer without user fields in input."""
    
    class Meta:
        model = Patient
        exclude = ['user']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return self.add_user_fields_to_representation(instance, representation)



class PatientDetailSerializer(PatientRepresentationMixin, BasePatientSerializer):
    medical_record = PatientMedicalRecordSerializer(required=False, partial=True)
    class Meta(BasePatientSerializer.Meta):
        fields = BasePatientSerializer.Meta.fields + ['medical_record']
        read_only_fields = ['id', 'medical_id']


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation = self.add_user_fields_to_representation(instance, representation)
        representation = self.add_medical_record_to_representation(instance, representation)
        return representation
    
    def update(self, instance, validated_data):
        """
        Update patient instance and related medical record.
        """
        return PatientService.update_patient_details_and_medical_record(instance, validated_data)


class DiagnosisSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient Diagnoses only. It is used in GroupedDiagnosisDetailsForPatientSerializer for grouping.
    It is not used in isolation  and does not contain detils, like caregiver, patient and organization unlike PatientDiagnosisDetailsSerializer
    """
    class Meta:
        model = PatientDiagnosisDetails
        fields = ['id', 'assessment', 'diagnoses', 'medication', 'health_allergies', 'health_care_center', 'notes', 'created_at']

class PatientDiagnosisSerializer(serializers.ModelSerializer):
    """
    Combines patient info with diagnoses.
    Handles three views via `view_type` context:
    - 'latest': Show only the latest diagnosis
    - 'all': Show all diagnoses
    """
    diagnoses = serializers.SerializerMethodField()
    patient_name = serializers.CharField(source="full_name", read_only=True)
    diagnosis_count = serializers.IntegerField(source="diagnoses.count", read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id',
            'patient_name',
            'medical_id',
            'diagnoses',
            'profile_picture',
            'address',
            'diagnosis_count',
        ]

    def get_diagnoses(self, obj):
        """
        Get diagnoses based on view type ('latest' or 'all').
        """
        view_type = self.context.get('view_type', 'all')
        diagnoses = obj.diagnoses.all() 

        if view_type == 'latest':
            latest_diagnosis = diagnoses.first()
            return (
                DiagnosisSerializer(latest_diagnosis, context=self.context).data
                if latest_diagnosis else None
            )
        return DiagnosisSerializer(diagnoses, many=True, context=self.context).data


class VitalSignSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSign
        fields = ['body_temperature', 'pulse_rate', 'blood_pressure', 'blood_oxygen', 'respiration_rate']

class PatientDiagnosisWithVitalSignSerializer(serializers.ModelSerializer):
    # Write-only fields for input
    patient_id = serializers.UUIDField(write_only=True, source='patient')
    caregiver_id = serializers.UUIDField(write_only=True, required=False, allow_null=True, source='caregiver')
    vital_sign = VitalSignSerializer(write_only=True, required=False)

    # Read-only relationship fields for response
    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    organization = serializers.PrimaryKeyRelatedField(read_only=True)
    caregiver = serializers.PrimaryKeyRelatedField(read_only=True)

    # Additional response fields
    vital_sign_data = serializers.SerializerMethodField()
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_profile_picture = serializers.SerializerMethodField()
    patient_medical_id = serializers.CharField(source='patient.medical_id', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    caregiver_name = serializers.CharField(source='caregiver.name', read_only=True)
    slug = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = PatientDiagnosisDetails
        fields = [
            'id', 'patient_id', 'caregiver_id', 'vital_sign',  # Write-only input fields
            'patient', 'organization', 'caregiver',  # Read-only relationship fields
            'assessment', 'health_care_center', 'diagnoses', 'medication', 'notes', 'health_allergies',
            'vital_sign_data', 'patient_name', 'patient_profile_picture', 'patient_medical_id',
            'organization_name', 'caregiver_name', 'slug', 'created_at'  # Additional response fields
        ]

    def get_patient_profile_picture(self, obj):
        if obj.patient and obj.patient.profile_picture:
            return obj.patient.profile_picture.url
        return None

    def get_vital_sign_data(self, obj):
        """Get vital sign data if exists"""
        try:
            if hasattr(obj, 'vitalsign') and obj.vitalsign:
                return VitalSignSerializer(obj.vitalsign).data
        except VitalSign.DoesNotExist:
            pass
        return None

    def create(self, validated_data):
        # Extract relationships that are passed from the viewset
        organization = validated_data.pop('organization', None)
        patient = validated_data.pop('patient', None)
        caregiver = validated_data.pop('caregiver', None)
        
        # These should be provided by perform_create
        if not all([organization, patient]):
            raise ValidationError("Organization and patient must be provided")

        # Use service to create diagnosis
        return PatientDiagnosisVitalSignService.create_diagnosis(
            patient, caregiver, organization, validated_data
        )

    def update(self, instance, validated_data):
        # Extract relationships if provided
        organization = validated_data.pop('organization', instance.organization)
        patient = validated_data.pop('patient', instance.patient)
        caregiver = validated_data.pop('caregiver', instance.caregiver)
        
        # Update the relationships
        instance.organization = organization
        instance.patient = patient
        instance.caregiver = caregiver
        
        # Use service to update diagnosis
        return PatientDiagnosisVitalSignService.update_diagnosis(instance, validated_data)


class PatientProfileSerializer(ValidationMixin, serializers.ModelSerializer):
    """Serializer for patient profile"""
    
    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'medical_id', 'date_of_birth', 
            'marital_status', 'profile_picture', 'gender', 'phone_number', 
            'emergency_phone_number', 'address', 
        ]
        read_only_fields = ['id', 'medical_id']

    def validate_first_name(self, value):
        return self.validate_name_field(value, "First name")

    def validate_last_name(self, value):
        return self.validate_name_field(value, "Last name")