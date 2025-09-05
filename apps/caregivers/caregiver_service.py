from django.db import transaction
from .models import Caregiver
from .utils import role_abbreviation

class CaregiverService:

    @staticmethod
    def generate_full_name(caregiver: Caregiver) -> str:
        return f"{caregiver.last_name} {caregiver.first_name}"

    @staticmethod
    def generate_full_name_with_role(caregiver: Caregiver) -> str:
        role_abbr = role_abbreviation.get(caregiver.caregiver_type, "")
        return f"{role_abbr.title()} {caregiver.first_name} {caregiver.last_name}"

    @staticmethod
    def generate_unique_staff_number(organization, caregiver_type):
        acronym = organization.acronym.upper()
        role_abbr = role_abbreviation.get(caregiver_type, "UNK")

        with transaction.atomic():
            last_number = Caregiver.objects.filter(
                organization=organization,
                caregiver_type=caregiver_type
            ).order_by('-id').first()
            if last_number and last_number.staff_number:
                last_count = int(last_number.staff_number.split("_")[-1])
            else:
                last_count = 0

            next_count = last_count + 1
            return f"{acronym}_{role_abbr}_{next_count}"
        
    @staticmethod
    def get_profile_picture_url(caregiver):
        try:
            return caregiver.profile_picture.url
        except:
            return ""
