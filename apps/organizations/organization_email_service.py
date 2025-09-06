from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.organizations.models import Organization
from shared.base_email_service import BaseEmailService
import logging

logger = logging.getLogger(__name__)

class OrganizationEmailService(BaseEmailService):
    """
    Handles organization-related emails (activation, invites, etc.).
    """

    @staticmethod
    def send_organization_activation_email(organization: Organization, current_site: str):
        user = organization.user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_link = f"{settings.REACT_FRONTEND_URL}/auth/verify-email/{uid}/{token}"

        context = {
            "organization_name": organization.name,
            "activation_link": activation_link,
            "current_site": current_site,
        }

        OrganizationEmailService.send_email(
            subject="Activate Your Organization Account",
            template="accounts/organizations/organization_activation_email.html",
            context=context,
            recipient_list=[user.email],
        )
    

    @staticmethod
    def send_patient_account_creation_notification_email(patient_email, patient_full_name, organization_name):
        login_url = f"{settings.REACT_FRONTEND_URL}/auth/login"

        context = {
            'organization_name': organization_name,
            'patient_email': patient_email,
            'patient_full_name': patient_full_name,
            'login_url': login_url,
        }

        subject = f"Welcome to {organization_name}, {patient_full_name}!"
        html_message = render_to_string('organizations/mails/patient_welcome_mail.html', context)

        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[patient_email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)