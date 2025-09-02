import uuid
from django.db import models
from django.shortcuts import render
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,Group, Permission
from django.utils.translation import gettext_lazy as _ 
from .managers import CustomUserManager
from .user_roles import UserRoles
from django.utils import timezone
from shared.models import SoftDeleteModel


class User(AbstractBaseUser,PermissionsMixin,SoftDeleteModel):
    pkid = models.BigAutoField(primary_key=True,editable=False,db_index=True)
    id = models.UUIDField(default=uuid.uuid4,editable=False,unique=True,db_index=True)
    email = models.EmailField(verbose_name=_("Email Address"),unique=True,db_index=True)
    role = models.CharField(max_length=20,choices=UserRoles.choices, null=True, blank=True,db_index=True)
    is_active = models.BooleanField(default=False,db_index=True)
    is_invited = models.BooleanField(default=False,db_index=True)
    is_verified = models.BooleanField(default=False,db_index=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True,blank=True,db_index=True)

    USERNAME_FIELD = "email"
   
    objects = CustomUserManager()

    class Meta:
        verbose_name = _("Customer Account")
        verbose_name_plural = _("Customer Accounts")
        ordering=["-created_at"]
        indexes = [
            models.Index(fields=["email", "deleted_at"]),
            models.Index(fields=["email", "is_active", "is_deleted"]),
            models.Index(fields=["is_verified", "is_active", "is_deleted"]),
            models.Index(fields=["role", "is_active", "is_deleted"]),
            models.Index(fields=["deleted_at"]),
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

        
   