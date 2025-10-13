import logging
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from apps.invites.exceptions import EmailSendingFailedException
from .invitation_email_service import InvitationEmailService
from .models import CaregiverInvite

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_invitation_to_caregiver(self, invitation_id, frontend_url=None):
    """
    Asynchronously sends a caregiver invitation email using the InvitationEmailService.
    """
    try:
    
        # Fetch the invitation object
        invitation = CaregiverInvite.objects.select_related("organization").get(id=invitation_id)

        # Delegate to the email service
        InvitationEmailService.send_caregiver_invitation_email(invitation, frontend_url)
        logger.info(f"Invitation email task completed for {invitation.email}")

    except CaregiverInvite.DoesNotExist:
        logger.error(f"Invitation with ID {invitation_id} not found.")
        raise EmailSendingFailedException(f"Invitation {invitation_id} not found.")

    except Exception as e:
        logger.error(f"Failed to send invitation email for {invitation_id}: {str(e)}")
        try:
            self.retry(countdown=60)
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for invitation {invitation_id}")
            raise EmailSendingFailedException(
                f"Failed to send invitation email after {self.max_retries} attempts."
            )
