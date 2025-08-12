import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class BaseAPIException(APIException):
    """Base exception class for consistent error responses"""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("A server error occurred.")
    default_code = "error"

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code:
            self.status_code = status_code
        super().__init__(detail, code)


class ValidationException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation failed."
    default_code = "validation_error"


class NotFoundException(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."
    default_code = "not_found"


class PermissionException(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "permission_denied"


class BusinessLogicException(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Business rule violation."
    default_code = "business_logic_error"


class AuthenticationException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication failed."
    default_code = "authentication_failed"


def custom_exception_handler(exc, context):
    """Custom exception handler for consistent error responses"""

    if isinstance(exc, DjangoValidationError):
        exc = ValidationException(detail=exc.messages[0] if exc.messages else str(exc))

    response = exception_handler(exc, context)
    if response is not None:
        # Log the error
        logger.error(
            f"API Error: {exc}",
            exc_info=True,
            extra={
                "view": context.get("view"),
                "request": context.get("request"),
                "args": context.get("args"),
                "kwargs": context.get("kwargs"),
            },
        )
        # Standardize error response format
        error_code = getattr(exc, "default_code", "error")
        error_detail = response.data

        # Extract detail message if it's in DRF format
        if isinstance(error_detail, dict) and "detail" in error_detail:
            error_detail = error_detail["detail"]
        elif isinstance(error_detail, dict):
            # Handle field validation errors
            error_detail = error_detail

        custom_response_data = {
            "success": False,
            "error": {
                "code": error_code,
                "message": str(error_detail)
                if not isinstance(error_detail, dict)
                else "Validation failed",
                "status_code": response.status_code,
                "details": error_detail if isinstance(error_detail, dict) else None,
            },
            "data": None,
        }

        response.data = custom_response_data

    return response
