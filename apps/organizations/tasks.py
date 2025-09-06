from celery import shared_task
from .organization_email_service import OrganizationEmailService
from apps.organizations.models import Organization
from .exceptions import OrganizationNotFoundException
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_organization_activation_email(current_site, organization_email):
    try:
        organization = Organization.objects.get(user__email=organization_email)
        OrganizationEmailService.send_organization_activation_email(organization, current_site)
    except Organization.DoesNotExist:
        raise OrganizationNotFoundException()

@shared_task
def send_patient_welcome_email( patient_email, patient_full_name, organization_name):
    """
    Sends a welcome email to a patient after their account is successfully created.
    """
    try:
        OrganizationEmailService.send_patient_account_creation_notification_email(patient_email, patient_full_name, organization_name, )
    except Exception as e:
        logger.error(f"Failed to send welcome email to {patient_email}: {str(e)}")
