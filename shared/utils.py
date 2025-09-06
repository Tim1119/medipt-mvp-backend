import logging
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)
User = get_user_model()

def get_user_from_uidb64(uidb64):
        try:
            # Decode the base64 string
            uid = urlsafe_base64_decode(uidb64).decode()
            
            # Validate that uid is numeric (for integer primary keys)
            if not uid.isdigit():
                logger.warning(f"Decoded UID is not numeric: {uid}")
                return None
            
            # Get the user
            return User.objects.get(pk=int(uid))
            
        except (ValueError, TypeError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to decode uidb64 '{uidb64}': {str(e)}")
            raise ValidationError("User does not exist")
        
        except User.DoesNotExist:
            logger.warning(f"User not found for UID: {uid}")
            raise ValidationError("User does not exist")
            
        except Exception as e:
            logger.error(f"Unexpected error decoding uidb64 '{uidb64}': {str(e)}")
            raise ValidationError("User does not exist")
            