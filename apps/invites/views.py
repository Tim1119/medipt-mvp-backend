import uuid
import logging
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from apps.organizations.permissions import IsOrganization
from apps.invites.models import CaregiverInvite, InvitationStatus
from apps.invites.serializers import CaregiverInvitationSerializer, CaregiverAcceptInvitationSerializer
from apps.invites.tasks import send_invitation_to_caregiver
from apps.invites.exceptions import (
    CaregiverInvitationException,
    ActiveInvitationExistsException,
    InvitationAlreadyAcceptedException,
    MaxResendsExceededException,
    EmailSendingFailedException,
    InvalidInvitationTokenException,
    InvitationNotFoundException,
    InvitationExpiredException,
)
from shared.validators import validate_uuid
from apps.caregivers.permissions import IsCaregiver
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)


def default_expires_at():
    return timezone.now() + timezone.timedelta(days=settings.INVITATION_EXPIRY_DAYS)


class InviteCaregiverView(CreateAPIView):
    """
    Allows an organization to invite a caregiver via email.
    Uses Celery for async email sending and handles re-invites safely.
    """
    serializer_class = CaregiverInvitationSerializer
    permission_classes = [IsAuthenticated, IsOrganization]
    throttle_classes = [UserRateThrottle]
    queryset = CaregiverInvite.objects.all()

    def perform_create(self, serializer):
        request = self.request
        email = serializer.validated_data["email"]
        role = serializer.validated_data["role"]
        max_resends = getattr(settings, "MAX_INVITATION_RESENDS", 3)

        with transaction.atomic():
            existing_invite = CaregiverInvite.objects.filter(
                email__iexact=email,
                organization=request.user.organization
            ).first()

            if existing_invite:
                if existing_invite.status == InvitationStatus.ACCEPTED:
                    raise InvitationAlreadyAcceptedException()
                if existing_invite.resend_count >= max_resends:
                    raise MaxResendsExceededException()
                if not existing_invite.is_expired():
                    raise ActiveInvitationExistsException()

                # Refresh the invitation
                existing_invite.token = uuid.uuid4()
                existing_invite.expires_at = default_expires_at()
                existing_invite.resend_count += 1
                existing_invite.status = InvitationStatus.PENDING
                existing_invite.invited_by = request.user
                existing_invite.save()
                invitation = existing_invite
            else:
                invitation = serializer.save(invited_by=request.user)

        # Send email asynchronously using Celery
        try:
            send_invitation_to_caregiver.delay(invitation.id)
            logger.info(f"Queued invitation email for {invitation.email} ({invitation.role})")
        except Exception as e:
            logger.error(f"Failed to queue invitation email for {invitation.email}: {e}")
            raise EmailSendingFailedException(
                detail={"message": "Invitation created, but email sending failed."}
            )

        return invitation

    def create(self, request, *args, **kwargs):
        """Overrides default create() to provide a custom success response."""
        try:
            response = super().create(request, *args, **kwargs)
            invitation = self.get_queryset().filter(email=request.data["email"]).last()
            return Response(
                {
                    "message": "Invitation created successfully. Email is being sent.", 
                    "data":{
                    "invitation_id": str(invitation.id),
                    "email": invitation.email,
                    "role": invitation.role,
                    "status": invitation.status,
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        except CaregiverInvitationException as e:
            raise e
        except Exception as e:
            logger.exception("Error while creating caregiver invitation.")
            raise CaregiverInvitationException(detail=str(e))





class CaregiverAcceptInvitationView(CreateAPIView):
    """
    Allows invited caregivers to accept their invitation and create an account.
    """
    serializer_class = CaregiverAcceptInvitationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def post(self, request, *args, **kwargs):
        token = self.kwargs.get("token")
        if not validate_uuid(token):
            raise InvalidInvitationTokenException()

        try:
            with transaction.atomic():
                invitation = CaregiverInvite.objects.filter(token=token).first()
                if not invitation:
                    raise InvitationNotFoundException()
                if invitation.is_expired():
                    invitation.status = InvitationStatus.EXPIRED
                    invitation.save()
                    raise InvitationExpiredException()
                if invitation.status != InvitationStatus.PENDING:
                    raise InvitationAlreadyAcceptedException()

                serializer = self.get_serializer(
                    data=request.data,
                    context={"token": token}
                )
                serializer.is_valid(raise_exception=True)
                caregiver = serializer.save()

                return Response(
                    {
                        "message": "Caregiver account created successfully.",
                        "data":{
                            "caregiver_id": str(caregiver.id),
                            "email": caregiver.user.email,
                            "organization": caregiver.organization.name,
                        }
                    },
                    status=status.HTTP_201_CREATED,
                )

        except CaregiverInvitationException as e:
            raise e  # Custom handled
        except Exception as e:
            raise CaregiverInvitationException(
                detail=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
