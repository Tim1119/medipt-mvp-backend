from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.organizations.models import Organization
from shared.base_email_service import BaseEmailService
from .models import User


class AccountEmailService(BaseEmailService):
    """
    Handles account-related emails (password reset, general notifications).
    """

    @staticmethod
    def send_password_reset_email(user: User):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_link = f"{settings.REACT_FRONTEND_URL}/auth/reset-password/{uid}/{token}"

        context = {
            "user_name": user.full_name if user.full_name else user.email,
            "reset_link": reset_link,
        }

        AccountEmailService.send_email(
            subject="Reset Your Password",
            template="accounts/general/password_reset_email.html",
            context=context,
            recipient_list=[user.email],
        )