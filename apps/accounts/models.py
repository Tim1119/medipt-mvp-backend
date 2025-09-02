import uuid
from django.db import models
from django.shortcuts import render
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,Group, Permission
from django.utils.translation import gettext_lazy as _ 
from .managers import CustomUserManager
from .user_roles import UserRoles
from django.utils import timezone


class User(AbstractBaseUser,PermissionsMixin):
    pkid = models.BigAutoField(primary_key=True,editable=False,db_index=True)
    id = models.UUIDField(default=uuid.uuid4,editable=False,unique=True,db_index=True)
    email = models.EmailField(verbose_name=_("Email Address"),unique=True,db_index=True)
    role = models.CharField(max_length=20,choices=UserRoles.choices, null=True, blank=True,db_index=True)
    is_active = models.BooleanField(default=False,db_index=True)
    is_invited = models.BooleanField(default=False,db_index=True)
    is_verified = models.BooleanField(default=False,db_index=True)
    is_organization_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True,blank=True,db_index=True)

    USERNAME_FIELD = "email"
   
    objects = CustomUserManager()

    class Meta:
        verbose_name = _("Customer Account")
        verbose_name_plural = _("Customer Accounts")
        ordering=["-created_at"]
        indexes = [
            models.Index(fields=["email", "deleted_at"]),
        ]
    
    @property
    def full_name(self):
        if self.role == UserRoles.ORGANIZATION and self.organization:
            return self.organization.full_name

        if self.role == UserRoles.CAREGIVER and self.caregiver:
            return self.caregiver.full_name

        if self.role == UserRoles.PATIENT and self.patient:
            return self.patient.full_name

        return self.email

        
    def delete(self):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()


    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save()
    

