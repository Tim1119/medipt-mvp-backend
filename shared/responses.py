from typing import Any, Dict, Optional

from rest_framework import status
from rest_framework.response import Response


class APIResponse:
    """Standardized API response format"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation successful",
        status_code: int = status.HTTP_200_OK,
        pagination: Optional[Dict] = None,
    ) -> Response:
        """Standard success response"""
        response_data = {"success": True, "message": message, "data": data}

        if pagination:
            response_data["pagination"] = pagination

        return Response(response_data, status=status_code)

    @staticmethod
    def error(
        message: str,
        code: str = "error",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        errors: Optional[Dict] = None,
    ) -> Response:
        """Standard error response"""
        response_data = {
            "success": False,
            "error": {"code": code, "message": message, "status_code": status_code},
            "data": None,
        }

        if errors:
            response_data["error"]["details"] = errors

        return Response(response_data, status=status_code)

    @staticmethod
    def created(
        data: Any = None, message: str = "Resource created successfully"
    ) -> Response:
        """Standard creation response"""
        return APIResponse.success(data, message, status.HTTP_201_CREATED)

    @staticmethod
    def no_content(message: str = "Operation completed successfully") -> Response:
        """Standard no content response"""
        return APIResponse.success(None, message, status.HTTP_204_NO_CONTENT)
