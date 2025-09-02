from django.db import models

# Create your models here.
from django.db import models
from shared.models import TimeStampedUUID
from autoslug import AutoSlugField
from django.utils.translation import gettext_lazy as _ 
from shared.validators import validate_phone_number,validate_organization_acronym
from apps.accounts.models import User
from cloudinary.models import CloudinaryField



class Organization(TimeStampedUUID):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255,verbose_name=_("Organization Name"),db_index=True)
    acronym = models.CharField(max_length=15,verbose_name=_("Organization Acronym"),unique=True,validators=[validate_organization_acronym])
    logo = CloudinaryField(
        'Organization logo',
        folder='organization_logo',
        default='default.png',
        allowed_formats=['jpg', 'png', 'jpeg'],
        transformation=[{'crop': 'limit', 'quality': 80}],
        blank=True,
        null=True
    )
    address = models.TextField(verbose_name=_("Organization's Address"),blank=True,null=True)
    phone_number=models.CharField(max_length=15,validators=[validate_phone_number],blank=True,null=True)
    slug = AutoSlugField(populate_from='name', unique=True)

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        ordering = ["-created_at"]

    
    @property
    def organization_logo_url(self):
        try:
            url = self.logo.url
        except:
            url ='' 
        return url
    

    def __str__(self):
        return f"Organization account for {self.name}"
    
    @property
    def full_name(self):
        return self.name
    