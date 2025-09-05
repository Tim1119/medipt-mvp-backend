from django.db import models
from django.forms import ValidationError
from shared.models import TimeStampedUUID
from autoslug import AutoSlugField
from django.utils.translation import gettext_lazy as _ 
from shared.validators import validate_phone_number
from shared.text_choices import Gender,MaritalStatus,CaregiverTypes
from apps.accounts.models import User
from apps.organizations.models import Organization
from .utils import role_abbreviation
from datetime import date
from cloudinary.models import CloudinaryField


class Caregiver(TimeStampedUUID):

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT,verbose_name=_("Organization"))
    first_name = models.CharField(max_length=255,verbose_name=_("Caregiver First Name"),db_index=True)
    last_name = models.CharField(max_length=255,verbose_name=_("Caregiver Last Name"),db_index=True)
    caregiver_type = models.CharField(max_length=30,choices=CaregiverTypes.choices,db_index=True)
    date_of_birth = models.DateField(blank=True,null=True)
    marital_status = models.CharField(max_length=30,choices=MaritalStatus.choices,verbose_name=_("Caregiver Marital Status"),blank=True,null=True)
    profile_picture = CloudinaryField(
        'image',
        folder='caregiver_profile_pictures',
        default='default.png',
        allowed_formats=['jpg', 'png', 'jpeg'],
         transformation=[{'crop': 'limit', 'quality': 80}],
    )
    gender = models.CharField(max_length=20,choices=Gender.choices,blank=True,null=True)
    phone_number=models.CharField(max_length=15,validators=[validate_phone_number],blank=True,null=True,db_index=True)
    address = models.TextField(verbose_name=_("Caregiver's Address"),blank=True,null=True)
    slug = AutoSlugField(populate_from='user', unique=True)
    staff_number = models.CharField(max_length=30, unique=True,blank=True,null=True)
    
    class Meta:
        verbose_name = _("Caregiver")
        verbose_name_plural = _("Caregivers")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Caregiver account for {self.first_name.title()} {self.last_name.title()} for {self.organization.name.title()} Organization"

    def save(self, *args, **kwargs):
        from .caregiver_service import CaregiverService
        if not self.staff_number:
            self.staff_number = CaregiverService.generate_unique_staff_number(
                self.organization, self.caregiver_type
            )
        super(Caregiver, self).save(*args, **kwargs)

    def clean(self):
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValidationError(_("Date of birth cannot be in the future."))
        
    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name}"
