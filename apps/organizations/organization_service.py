from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from apps.organizations.models import Organization, User
from shared.text_choices import UserRoles
import logging
from apps.patients.models import Patient,PatientMedicalRecord
from .tasks import send_patient_welcome_email

logger = logging.getLogger(__name__)


class OrganizationService:

    @staticmethod
    def organization_logo_url(caregiver):
        try:
            url = caregiver.logo.url
        except:
            url ='' 
        return url

    @staticmethod
    def create_organization(name, acronym, email, password):
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    role=UserRoles.ORGANIZATION
                )

                organization = Organization.objects.create(
                    user=user,
                    name=name.title(),
                    acronym=acronym,
                )
            return organization

        except IntegrityError as e:
            logger.error(f"Database error during organization creation: {e}", exc_info=True)
            raise ValidationError("A database integrity error occurred. Please check the data and try again.")

        except ValidationError as e:
            logger.warning(f"Validation error: {e}", exc_info=True)
            raise e

        except Exception as e:
            logger.critical(f"Unexpected error: {e}", exc_info=True)
            raise ValidationError("An unexpected error occurred. Please try again later.")
        
    @staticmethod
    @transaction.atomic
    def create_patient_for_organization(data, organization):

        # Extract nested data
        email = data.pop('email')
        password = data.pop('password')
        medical_record_data = data.pop('medical_record', {})

        # Validate email uniqueness
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")

        # Create user
        user = User.objects.create_user(email=email,password=password,role=UserRoles.PATIENT,is_active=True,is_verified=True)

        # Create patient
        patient = Patient.objects.create(user=user,organization=organization,**data)

        # Create medical record
        PatientMedicalRecord.objects.create(patient=patient, **medical_record_data)

        # Send notification email asynchronously
        send_patient_welcome_email.delay(
            patient_email=user.email,
            patient_full_name=f"{patient.first_name} {patient.last_name}",
            organization_name=organization.name,
        )

        return patient
