from celery import shared_task
from .organization_email_service import OrganizationEmailService
from apps.organizations.models import Organization
from .exceptions import OrganizationNotFoundException


@shared_task
def send_organization_activation_email(current_site, organization_email):
    try:
        organization = Organization.objects.get(user__email=organization_email)
        OrganizationEmailService.send_organization_activation_email(organization, current_site)
    except Organization.DoesNotExist:
        raise OrganizationNotFoundException()

