import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.tokens import default_token_generator

# from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from shared.models import TimestampedModel

from .managers import CustomUserManager
from .user_roles import UserRoles


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    """Enhanced User model with comprehensive security features"""

    # Primary fields
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    email = models.EmailField(
        verbose_name=_("Email Address"), unique=True, db_index=True
    )
    role = models.CharField(
        max_length=20, choices=UserRoles.choices, null=True, blank=True, db_index=True
    )

    # Status fields
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Designates whether this user should be treated as active."),
    )
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Designates whether the user has verified their email address."),
    )
    is_invited = models.BooleanField(
        default=False,
        help_text=_("Designates whether the user was invited to the system."),
    )
    is_organization_admin = models.BooleanField(
        default=False,
        help_text=_("Designates whether the user is an organization admin."),
    )
    is_staff = models.BooleanField(
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )

    # Security and audit fields
    email_verified_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True, db_index=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)

    # Password reset fields
    password_reset_token = models.CharField(max_length=100, null=True, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)

    # Two-factor authentication
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, null=True, blank=True)
    backup_tokens = models.JSONField(default=list, blank=True)

    # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    USERNAME_FIELD = "email"
    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["role", "is_verified"]),
            models.Index(fields=["is_active", "is_verified", "role"]),
            models.Index(fields=["created_at", "role"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(email__isnull=False) & ~models.Q(email=""),
                name="email_not_empty",
            )
        ]

    def clean(self):
        """Custom model validation"""
        super().clean()
        if self.email:
            self.email = self.email.lower().strip()

        # Validate role-specific requirements
        if self.role == UserRoles.ORGANIZATION and not self.is_organization_admin:
            self.is_organization_admin = True

    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()

        # Set password_changed_at if password is being set
        if self.pk is None or "password" in kwargs.get("update_fields", []):
            self.password_changed_at = timezone.now()

        super().save(*args, **kwargs)

    # Security properties
    @property
    def is_deleted(self):
        """Check if user is soft deleted"""
        return self.deleted_at is not None

    @property
    def is_locked(self):
        """Check if account is currently locked"""
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False

    @property
    def is_email_verified(self):
        """Check if email is verified"""
        return self.email_verified_at is not None

    # Security methods
    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.locked_until = timezone.now() + timezone.timedelta(
            minutes=duration_minutes
        )
        self.save(update_fields=["locked_until"])

    def unlock_account(self):
        """Unlock account and reset failed attempts"""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=["locked_until", "failed_login_attempts"])

    def increment_failed_login(self):
        """Increment failed login attempts and lock if necessary"""
        self.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account(duration_minutes=30)

        self.save(update_fields=["failed_login_attempts", "locked_until"])

    def reset_failed_login_attempts(self):
        """Reset failed login attempts on successful login"""
        if self.failed_login_attempts > 0:
            self.failed_login_attempts = 0
            self.save(update_fields=["failed_login_attempts"])

    def verify_email(self):
        """Mark email as verified"""
        self.email_verified_at = timezone.now()
        self.is_verified = True
        self.is_active = True  # Activate account when email is verified
        self.save(update_fields=["email_verified_at", "is_verified", "is_active"])

    def soft_delete(self):
        """Soft delete the user"""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["deleted_at", "is_active"])

    def restore(self):
        """Restore soft-deleted user"""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    # Token methods
    def generate_verification_token(self):
        """Generate email verification token using Django's built-in token generator"""
        return default_token_generator.make_token(self)

    def get_verification_uid(self):
        """Get UID for email verification"""
        return urlsafe_base64_encode(force_bytes(self.pk))

    def check_verification_token(self, token):
        """Check if verification token is valid"""
        return default_token_generator.check_token(self, token)

    def generate_password_reset_token(self):
        """Generate password reset token"""
        token = default_token_generator.make_token(self)
        self.password_reset_token = token
        self.password_reset_expires = timezone.now() + timezone.timedelta(hours=1)
        self.save(update_fields=["password_reset_token", "password_reset_expires"])
        return token

    def check_password_reset_token(self, token):
        """Check if password reset token is valid"""
        if (
            self.password_reset_token == token
            and self.password_reset_expires
            and timezone.now() < self.password_reset_expires
        ):
            return True
        return False

    def clear_password_reset_token(self):
        """Clear password reset token after use"""
        self.password_reset_token = None
        self.password_reset_expires = None
        self.save(update_fields=["password_reset_token", "password_reset_expires"])

    # Permission methods
    def has_permission(self, permission_name):
        """Check if user has a specific permission"""
        permissions = UserRoles.get_role_permissions(self.role)
        return permissions.get(permission_name, False)

    def get_all_permissions(self):
        """Get all permissions for this user's role"""
        return UserRoles.get_role_permissions(self.role)

    # Utility properties
    @property
    def full_name(self):
        """Get user's full name based on role with error handling"""
        try:
            if self.role == UserRoles.ORGANIZATION and hasattr(self, "organization"):
                return self.organization.name
            elif self.role == UserRoles.CAREGIVER and hasattr(self, "caregiver"):
                return self.caregiver.full_name
            elif self.role == UserRoles.PATIENT and hasattr(self, "patient"):
                return self.patient.full_name
        except AttributeError:
            pass
        return self.email

    @property
    def short_name(self):
        """Get user's short name"""
        return self.email.split("@")[0]

    def get_organization(self):
        """Get the organization this user belongs to"""
        try:
            if self.role == UserRoles.ORGANIZATION:
                return self.organization
            elif self.role == UserRoles.CAREGIVER:
                return self.caregiver.organization
            elif self.role == UserRoles.PATIENT:
                return self.patient.organization
        except AttributeError:
            pass
        return None

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    def __repr__(self):
        return f"<User: {self.email} - {self.role}>"


class EmailVerificationToken(TimestampedModel):
    """Model to track email verification tokens"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verification_tokens"
    )
    token = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = _("Email Verification Token")
        verbose_name_plural = _("Email Verification Tokens")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.user.generate_verification_token()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(
                hours=24
            )  # 24 hour expiry
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if token is expired"""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"Verification token for {self.user.email}"


class PasswordResetToken(TimestampedModel):
    """Model to track password reset tokens"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    token = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = _("Password Reset Token")
        verbose_name_plural = _("Password Reset Tokens")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.user.generate_verification_token()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(
                hours=1
            )  # 1 hour expiry
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if token is expired"""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"Password reset token for {self.user.email}"


class LoginSession(TimestampedModel):
    """Model to track user login sessions"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="login_sessions"
    )
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    logged_out_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Login Session")
        verbose_name_plural = _("Login Sessions")
        ordering = ["-created_at"]

    def logout(self):
        """Mark session as logged out"""
        self.is_active = False
        self.logged_out_at = timezone.now()
        self.save(update_fields=["is_active", "logged_out_at"])

    def __str__(self):
        return f"Session for {self.user.email} from {self.ip_address}"
