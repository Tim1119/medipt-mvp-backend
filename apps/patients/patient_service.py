from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from apps.organizations.models import Organization, User
from shared.text_choices import UserRoles
import logging
from apps.patients.models import Patient,PatientMedicalRecord


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

       