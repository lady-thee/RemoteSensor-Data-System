import uuid
from datetime import timedelta
from collections.abc import Iterable

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, BaseUserManager, Group)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("Email must be provided!")
        kwargs.setdefault("is_active", True)
        kwargs.setdefault("is_superuser", False)

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        operator_group, _ = Group.objects.get_or_create(name="Operator")
        user.groups.add(operator_group)
        return user

    def create_superuser(self, email, password, **kwargs):
        if not email:
            raise ValueError("Email must be provided!")
        kwargs.setdefault("is_active", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_verified", True)

        superuser = self.model(email=self.normalize_email(email), **kwargs)
        superuser.set_password(password)
        superuser.save(using=self._db)
        return superuser


class AccountTypes(models.TextChoices):
    INDIVIDUAL = "INDIVIDUAL", "Individual"
    COMPANY = "COMPANY", "Company"

class AccountStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    SUSPENDED = "SUSPENDED", "Suspended"


class SubscriptionPlan(models.TextChoices):
    FREE = "FREE", "Free"
    STANDARD = "STANDARD", "Standard"
    ENTERPRISE = "ENTERPRISE", "Enterprise"


class Account(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False
    )
    email = models.EmailField(db_index=True, unique=True, max_length=200, blank=False)
    is_verified = models.BooleanField(default=False)
    account_type = models.CharField(max_length=20, choices=AccountTypes.choices, default=AccountTypes.INDIVIDUAL)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    residence = models.CharField(max_length=250, blank=True)
    activation_code = models.CharField(max_length=200, blank=True, null=True)
    activation_code_created_at = models.DateTimeField(null=True, blank=True)
    reset_password_code = models.CharField(max_length=200, blank=True, null=True)
    reset_password_code_created_at = models.DateTimeField(null=True, blank=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    subscription_plan = models.CharField(max_length=20, choices=SubscriptionPlan.choices, default=SubscriptionPlan.FREE)
    status = models.CharField(max_length=20, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    # data_retention_days = models.PositiveIntegerField(default=30)
    bio = models.TextField(blank=True, null=True)
    settings = models.JSONField(default=dict, blank=True)
    # billing_info = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="custom_user_set", 
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="custom_user_permissions_set",
        related_query_name="custom_user_permission",
    )

    class Meta:
        unique_together = ["id", "email"]

    def __str__(self) -> str:
        return self.email
    
    def is_activation_code_expired(self) -> bool:
        expiry_time = self.activation_code_created_at + timedelta(minutes=30)
        return self.activation_code_created_at > expiry_time
    
    def is_reset_password_token_expired(self) -> bool:
        expiry_time = self.reset_password_code_created_at + timedelta(minutes=30)
        return self.reset_password_code_created_at > expiry_time


class CompanyProfile(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False
    )
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="company_profile")
    industry = models.CharField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name