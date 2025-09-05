from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.types import ErrorResponse

class MyExceptionFormatter(ExceptionFormatter):
    """
    Custom exception formatter to structure error responses
    """
    def format_error_response(self, error_response: ErrorResponse):
        error_messages = []
        
        # Extract error code more robustly
        error_code = self._get_error_code(error_response)
            
        for error in error_response.errors:
            if (
                error_response.type == "validation_error" 
                and error.attr != "non_field_errors" 
                and error.attr is not None
            ):
                error_messages.append(f"{error.attr}: {error.detail}")
            else:
                error_messages.append(error.detail)

        return {
            "success": False,
            "type": error_response.type,
            "code": error_code,
            "errors": error_messages
        }
    
    def _get_error_code(self, error_response: ErrorResponse):
        """Extract error code from various sources"""
        # Try to get code from the first error
        if error_response.errors:
            first_error = error_response.errors[0]
            if hasattr(first_error, 'code') and first_error.code:
                return first_error.code
        
        # Try to get from the original exception if available
        if hasattr(self, 'exc') and hasattr(self.exc, 'default_code'):
            return self.exc.default_code
            
        # Fall back to error type
        return error_response.type