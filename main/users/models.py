import uuid
from collections.abc import Iterable

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("Email must be provided!")
        kwargs.setdefault("is_active", True)
        kwargs.setdefault("is_superuser", False)
        kwargs.setdefault("is_staff", False)

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
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_verified", True)

        superuser = self.model(email=self.normalize_email(email), **kwargs)
        superuser.set_password(password)
        superuser.save(using=self._db)
        return superuser


class User(AbstractUser):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False
    )
    email = models.EmailField(db_index=True, unique=True, max_length=200, blank=False)
    is_verified = models.BooleanField(default=False)
    # company_name = models.CharField(max_length=252, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    residence = models.CharField(max_length=250, blank=True)
    
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
