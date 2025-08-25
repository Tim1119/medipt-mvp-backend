from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRoles(models.TextChoices):
    ORGANIZATION = "ORGANIZATION", _("Organization")
    CAREGIVER = "CAREGIVER", _("Caregiver")
    PATIENT = "PATIENT", _("Patient")