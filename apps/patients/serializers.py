import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email as django_validate_email, RegexValidator
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .mixins import ValidationMixin
# from apps.accounts.user_roles import UserRoles
# from .exceptions import PatientNotificationFailedException
from .mixins import PatientRepresentationMixin
from .models import Patient, PatientMedicalRecord, PatientDiagnosisDetails, VitalSign
from .patient_service import PatientService


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




# class PatientDetailSerializer(PatientRepresentationMixin, BasePatientSerializer):
#     """Detailed patient serializer with medical records for updates."""
    
#     medical_record = PatientMedicalRecordSerializer(required=False, partial=True)

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         representation = self.add_user_fields_to_representation(instance, representation)
#         representation = self.add_medical_record_to_representation(instance, representation)
#         return representation
    
#     def update(self, instance, validated_data):
#         """Update patient instance and related medical record."""
#         medical_record_data = validated_data.pop('medical_record', None)
        
#         with transaction.atomic():
#             # Update patient fields
#             for attr, value in validated_data.items():
#                 setattr(instance, attr, value)
#             instance.save()
            
#             # Update or create medical record
#             if medical_record_data:
#                 PatientMedicalRecord.objects.update_or_create(
#                     patient=instance,
#                     defaults=medical_record_data
#                 )
                
#         return instance


# class VitalSignSerializer(serializers.ModelSerializer):
#     """Serializer for vital signs data."""
    
#     class Meta:
#         model = VitalSign
#         fields = [
#             'body_temperature', 'pulse_rate', 'blood_pressure', 
#             'blood_oxygen', 'respiration_rate', 'weight'
#         ]


# class DiagnosisSerializer(serializers.ModelSerializer):
#     """Basic diagnosis serializer for grouping purposes."""
    
#     class Meta:
#         model = PatientDiagnosisDetails
#         fields = [
#             'id', 'assessment', 'diagnoses', 'medication', 'health_allergies', 
#             'health_care_center', 'notes', 'created_at'
#         ]


# class PatientDiagnosisSerializer(serializers.ModelSerializer):
#     """
#     Patient serializer with diagnosis information.
#     Supports different view types: 'latest' for list page, 'all' for history.
#     """
    
#     diagnoses = serializers.SerializerMethodField()
#     patient_profile_picture = serializers.SerializerMethodField()
#     patient_name = serializers.CharField(source='full_name', read_only=True)
#     diagnosis_count = serializers.SerializerMethodField()

#     class Meta:
#         model = Patient
#         fields = [
#             'id', 'patient_name', 'medical_id', 'diagnoses', 
#             'patient_profile_picture', 'address', 'diagnosis_count'
#         ]

#     def get_diagnoses(self, obj):
#         """Get diagnosis details based on view type."""
#         view_type = self.context.get('view_type', 'all')
#         diagnoses = self._get_patient_diagnoses(obj)

#         if view_type == 'latest':
#             latest_diagnosis = diagnoses.first()
#             return DiagnosisSerializer([latest_diagnosis], many=True, context=self.context).data if latest_diagnosis else []
        
#         return DiagnosisSerializer(diagnoses, many=True, context=self.context).data

#     def get_diagnosis_count(self, obj):
#         """Get total count of diagnoses for this patient."""
#         return self._get_patient_diagnoses(obj).count()

#     def get_patient_profile_picture(self, obj):
#         """Get the patient's profile picture URL."""
#         return self._get_absolute_url(obj.profile_picture)

#     def _get_patient_diagnoses(self, obj):
#         """Helper method to get patient diagnoses queryset."""
#         if hasattr(obj, 'patientdiagnosisdetails_set'):
#             return obj.patientdiagnosisdetails_set.all().order_by('-created_at')
#         return PatientDiagnosisDetails.objects.filter(patient=obj).order_by('-created_at')

#     def _get_absolute_url(self, file_field):
#         """Helper method to get absolute URL for file fields."""
#         if file_field:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri(file_field.url)
#             return file_field.url
#         return None


# class SingleDiagnosisSerializer(serializers.ModelSerializer):
#     """Detailed serializer for single diagnosis view."""
    
#     patient_name = serializers.CharField(source='patient.full_name', read_only=True)
#     patient_medical_id = serializers.CharField(source='patient.medical_id', read_only=True)
#     patient_profile_picture = serializers.SerializerMethodField()
#     organization_name = serializers.CharField(source='organization.name', read_only=True)
#     caregiver_name = serializers.CharField(source='caregiver.full_name_with_role', read_only=True)
#     caregiver_id = serializers.CharField(source='caregiver.id', read_only=True)
#     vital_signs = serializers.SerializerMethodField()

#     class Meta:
#         model = PatientDiagnosisDetails
#         fields = [
#             'id', 'patient_name', 'patient_medical_id', 'patient_profile_picture',
#             'organization_name', 'caregiver_name', 'caregiver_id', 'assessment',
#             'diagnoses', 'medication', 'health_allergies', 'health_care_center',
#             'notes', 'vital_signs', 'created_at', 'updated_at'
#         ]

#     def get_patient_profile_picture(self, obj):
#         """Get the patient's profile picture URL."""
#         if obj.patient.profile_picture:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri(obj.patient.profile_picture.url)
#             return obj.patient.profile_picture.url
#         return None

#     def get_vital_signs(self, obj):
#         """Get vital signs associated with this diagnosis."""
#         try:
#             vital_signs = obj.vitalsign
#             return VitalSignSerializer(vital_signs).data
#         except VitalSign.DoesNotExist:
#             return None


# class PatientDiagnosisWithVitalSignSerializer(serializers.ModelSerializer):
#     """Serializer for creating/updating diagnosis with vital signs."""
    
#     # Write-only fields
#     vital_sign = VitalSignSerializer(write_only=True, required=False)
    
#     # Read-only fields
#     patient_name = serializers.CharField(source='patient.full_name', read_only=True)
#     patient_profile_picture = serializers.SerializerMethodField()
#     patient_medical_id = serializers.CharField(source='patient.medical_id', read_only=True)
#     organization_name = serializers.CharField(source='organization.name', read_only=True)
#     caregiver_name = serializers.CharField(source='caregiver.name', read_only=True)

#     class Meta:
#         model = PatientDiagnosisDetails
#         fields = [
#             'id', 'patient', 'organization', 'caregiver', 'assessment', 
#             'health_care_center', 'diagnoses', 'medication', 'notes', 
#             'health_allergies', 'vital_sign', 'patient_name', 
#             'patient_profile_picture', 'patient_medical_id', 
#             'organization_name', 'caregiver_name', 'slug', 'created_at'
#         ]
#         read_only_fields = ['patient', 'organization', 'caregiver', 'slug', 'created_at']

#     def get_patient_profile_picture(self, obj):
#         """Get patient's profile picture URL."""
#         if obj.patient.profile_picture:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri(obj.patient.profile_picture.url)
#             return obj.patient.profile_picture.url
#         return None

#     def create(self, validated_data):
#         """Create diagnosis with optional vital signs."""
#         vital_sign_data = validated_data.pop('vital_sign', None)
        
#         try:
#             with transaction.atomic():
#                 patient_diagnosis = PatientDiagnosisDetails.objects.create(**validated_data)
#                 if vital_sign_data:
#                     VitalSign.objects.create(
#                         patient_diagnoses_details=patient_diagnosis, 
#                         **vital_sign_data
#                     )
#                 return patient_diagnosis
#         except IntegrityError as e:
#             raise ValidationError(f"Database error: {str(e)}")

#     def update(self, instance, validated_data):
#         """Update diagnosis with optional vital signs."""
#         vital_sign_data = validated_data.pop('vital_sign', None)
        
#         try:
#             with transaction.atomic():
#                 # Update diagnosis fields
#                 for attr, value in validated_data.items():
#                     setattr(instance, attr, value)
#                 instance.save()

#                 # Update or create vital signs
#                 if vital_sign_data:
#                     VitalSign.objects.update_or_create(
#                         patient_diagnoses_details=instance,
#                         defaults=vital_sign_data
#                     )
#                 return instance
#         except IntegrityError as e:
#             raise ValidationError(f"Database error: {str(e)}")


# class PatientBasicInfoSerializer(serializers.ModelSerializer):
#     """Basic patient information serializer."""
    
#     patient_name = serializers.CharField(source='full_name', read_only=True)
#     profile_picture = serializers.SerializerMethodField()

#     class Meta:
#         model = Patient
#         fields = ['id', 'patient_name', 'medical_id', 'profile_picture']

#     def get_profile_picture(self, obj):
#         """Get profile picture URL."""
#         return obj.profile_picture_url