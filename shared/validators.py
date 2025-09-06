import re,uuid
from django.core.exceptions import ValidationError

def validate_phone_number(value):
    nigerian_phone_regex = re.compile(r'^(?:\+234|0)[789]\d{9}$')

    if not nigerian_phone_regex.match(value):
        raise ValidationError(
            'Enter a valid Nigerian phone number. It should start with +234 or 0 and contain 10 digits.'
        )
    
def validate_uuid(id, version=None):
    try:
        uuid_str = str(id)
        uuid_obj = uuid.UUID(uuid_str)
        if version is not None:
            return uuid_obj.version == version
        return True
    except (ValueError, AttributeError, TypeError):
        return False

def validate_organization_acronym(value):
    if len(value) < 2 or len(value) > 15:
        raise ValidationError("Organization acronym must be between 2 and 15 characters.")

def validate_blood_pressure(value):
    if not re.match(r'^\d{2,3}/\d{2,3}$', value):
        raise ValidationError("Enter a valid blood pressure in the format '120/80'.")