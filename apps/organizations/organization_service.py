from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from apps.organizations.models import Organization, User
from shared.text_choices import UserRoles
import logging

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
