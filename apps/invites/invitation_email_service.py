import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from shared.base_email_service import BaseEmailService

logger = logging.getLogger(__name__)


import logging
from django.conf import settings
from shared.base_email_service import BaseEmailService

logger = logging.getLogger(__name__)


class InvitationEmailService(BaseEmailService):
    """
    Handles sending caregiver invitation emails.
    Extends BaseEmailService for consistency across all email flows.
    """

    @staticmethod
    def send_caregiver_invitation_email(invitation, frontend_url=None):
        accept_link = f"{frontend_url or settings.REACT_FRONTEND_URL}/caregivers/accept-invitation/{invitation.token}"
        context = {
            "organization_name": invitation.organization.name,
            "invitation_email": invitation.email,
            "invitation_role": invitation.role,
            "accept_link": accept_link,
            "expiry_days": getattr(settings, "INVITATION_EXPIRY_DAYS", 7),
        }

        try:
            InvitationEmailService.send_email(
                subject=f"Invitation to join {invitation.organization.name} as a {invitation.role}",
                template="invites/emails/caregiver_invitation_email.html",
                context=context,
                recipient_list=[invitation.email],
            )
            logger.info(f"Sent caregiver invitation to {invitation.email}")
        except Exception as e:
            logger.error(f"Failed to send caregiver invitation to {invitation.email}: {e}")
