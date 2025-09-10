from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from apps.organizations.models import Organization, User
from shared.text_choices import UserRoles
import logging
from apps.patients.models import Patient,PatientMedicalRecord
from .models import PatientDiagnosisDetails,VitalSign


logger = logging.getLogger(__name__)


class PatientService:

    @staticmethod
    def update_patient_details_and_medical_record(instance, validated_data):
        medical_record_data = validated_data.pop('medical_record', None)

        try:
            with transaction.atomic():
                # Update patient fields
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()

                # Update or create medical record
                if medical_record_data:
                    PatientMedicalRecord.objects.update_or_create(
                        patient=instance,
                        defaults=medical_record_data
                    )

                return instance

        except IntegrityError as e:
            logger.error(f"Integrity error updating patient {instance.id}: {e}")
            raise ValidationError("Could not update patient details.")


class PatientDiagnosisVitalSignService:
    @staticmethod
    def create_diagnosis(patient, caregiver, organization, validated_data):
        vital_sign_data = validated_data.pop('vital_sign', None)
        try:
            with transaction.atomic():
                diagnosis = PatientDiagnosisDetails.objects.create(
                    patient=patient,
                    caregiver=caregiver,
                    organization=organization,
                    **validated_data
                )
                if vital_sign_data:
                    VitalSign.objects.create(
                        patient_diagnoses_details=diagnosis,
                        **vital_sign_data
                    )
            return diagnosis
        except IntegrityError as e:
            raise ValidationError(f"Error creating diagnosis: {str(e)}")

    @staticmethod
    def update_diagnosis(instance, validated_data):
        vital_sign_data = validated_data.pop('vital_sign', None)
        try:
            with transaction.atomic():
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()

                if vital_sign_data:
                    VitalSign.objects.update_or_create(
                        patient_diagnoses_details=instance,
                        defaults=vital_sign_data
                    )
            return instance
        except IntegrityError as e:
            raise ValidationError(f"Error updating diagnosis: {str(e)}")