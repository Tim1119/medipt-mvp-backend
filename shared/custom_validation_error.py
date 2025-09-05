from rest_framework.exceptions import APIException

class CustomValidationError(APIException):
    """
    Custom exception to handle validation errors with a consistent structure.
    """
    status_code = 400
    default_detail = "Validation error occurred."
    default_code = "validation_error"

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code:
            self.status_code = status_code
        
        # Fix: Handle the detail and code properly
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
            
        # Pass only detail to parent, set code separately
        super().__init__(detail)
        self.default_code = code
