from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):

    def email_validator(self,email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("You must provide a valide email address"))

    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError(_("User must provide and email address"))
        if not password:
            raise ValueError(_("User must provide a password"))
        
        self.model(email=self.normalize_email(),)
        


