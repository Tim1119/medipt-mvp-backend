from django.db import IntegrityError
from django.forms import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from shared.custom_validation_error import CustomValidationError
from .serializers import OrganizationSignupSerializer,LoginSerializer
from .models import User
from apps.organizations.tasks import send_organization_activation_email,send_password_reset_email
from django.contrib.sites.shortcuts import get_current_site
import jwt
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .user_roles import UserRoles
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .exceptions import OrganizationSignupException, OrganizationVerificationEmailFailedException
import logging

logger = logging.getLogger(__name__)


class OrganizationSignupView(generics.GenericAPIView):
    serializer_class = OrganizationSignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)  # cleaner

        try:
            organization = serializer.save()
            organization_email = organization.user.email
            current_site_domain = get_current_site(request).domain

            # Async email send
            try:
                send_organization_activation_email.delay(current_site_domain, organization_email)
            except Exception as email_error:
                logger.error(f"Email sending failed: {email_error}", exc_info=True)
                raise OrganizationVerificationEmailFailedException()

            return Response({"message": "Organization registered successfully", "data": serializer.data},status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            raise OrganizationSignupException(detail="Organization already exists.")
        except ValidationError as e:
            raise OrganizationSignupException(detail=e.messages)
        except Exception as e:
            raise OrganizationSignupException(detail=f"Unexpected error: {str(e)}")
