from django.db import IntegrityError
from django.forms import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import OrganizationSignupSerializer
from .models import User
from apps.organizations.tasks import send_organization_activation_email
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status
from rest_framework.response import Response
from .exceptions import InvalidActivationTokenException, OrganizationSignupException, OrganizationVerificationEmailFailedException, UserDoesNotExistException
import logging
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

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


class VerifyAccount(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            if user.is_active:
                return Response({"success": True, "message": "Account already active."})

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.is_verified = True
                user.save()
                return Response({"success": True, "message": "Account successfully activated."})
            else:
                raise InvalidActivationTokenException()
        
        except User.DoesNotExist:
            raise UserDoesNotExistException()
        
