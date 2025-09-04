from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken

from medipt.apps.accounts.email_service import OrganizationEmailService
from .models import User
from apps.organizations.models import Organization
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime, timedelta,timezone
from .exceptions import OrganizationNotFoundException
import jwt


@shared_task
def send_organization_activation_email(current_site, organization_email):
    try:
        organization = Organization.objects.get(user__email=organization_email)
        OrganizationEmailService.send_activation_email(organization, current_site)
    except Organization.DoesNotExist:
        raise OrganizationNotFoundException()

