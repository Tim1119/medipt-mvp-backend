from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.organizations.models import Organization

class OrganizationEmailService:

    @staticmethod
    def send_organization_activation_email(organization: Organization, current_site: str):
        """
        Generates a one-time activation token and sends an email to the organization user.
        """
        user = organization.user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_link = f"{settings.REACT_FRONTEND_URL}/auth/verify-email/{uid}/{token}"

        context = {
            'organization_name': organization.name,
            'activation_link': activation_link,
            'current_site': current_site,
        }

        subject = 'Activate Your Organization Account'
        html_message = render_to_string(
            'accounts/organizations/organization_activation_email.html',
            context
        )

        from_email = settings.EMAIL_HOST_USER
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=from_email,
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
