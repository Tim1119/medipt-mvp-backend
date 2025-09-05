# tasks.py
from celery import shared_task
from apps.accounts.models import User
from .email_service import AccountEmailService
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_password_reset_email(user_email: str):
    try:
        user = User.objects.get(email=user_email)
        AccountEmailService.send_password_reset_email(user)
    except User.DoesNotExist:
        logger.warning(f"Password reset requested for non-existent email: {user_email}")
