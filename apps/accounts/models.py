from django.db import models
from shared.models import BaseModel,TimeStampedModel,SoftDeleteModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.tokens import default_token_generator
import uuid
from django.utils.translation import gettext_lazy as _
from .user_roles import UserRoles

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin,TimeStampedModel):
    pkid = models.BigAutoField(primary_key=True,editable=False)
    id = models.UUIDField(editable=False,unique=True,default=uuid.uuid4,db_index=True)
    email = models.EmailField(verbose_name=_("Email Adress"),unique=True,db_index=True,)
    role = models.CharField(default=UserRoles.PATIENT,verbose_name=_(" User Role"),choices=UserRoles.choices,db_index=True)

    #status fields
    is_active = models.BooleanField(help_text=_('Is user active?'),default=False,db_index=True)
    is_staff = models.BooleanField(help_text=_('Is user a staff?'),default=False,db_index=True)
    is_verified = models.BooleanField(help_text=_('Is User verified?'),default=False,db_index=True)
    is_invited =  models.BooleanField(help_text=_('was user invited?'),default=False,db_index=True)
    is_organization_admin =  models.BooleanField(help_text=_('is user organization admin?'),default=False,db_index=True)

    two_factor_enabled = models.BooleanField(default=False)
    last_2fa_verified = models.DateTimeField(blank=True, null=True)


    USERNAME_FIELD = "email"
    objects = 





    
