from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.organizations.models import Organization, User


class BaseEmailService:
    """
    Provides shared utilities for sending HTML emails.
    Specialized services (activation, reset, etc.) extend this.
    """

    @staticmethod
    def send_email(subject: str, template: str, context: dict, recipient_list: list):
        html_message = render_to_string(template, context)

        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=recipient_list,
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)