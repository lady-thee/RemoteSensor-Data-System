from collections.abc import Iterable
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.utils.translation import gettext as _
from django.utils import timezone
import uuid



class UserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('Email must be provided!')
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_superuser', False)
        kwargs.setdefault('is_staff', False)
        
        user = self.model(
            email = self.normalize_email(email),
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user 
    
    def create_superuser(self, email, password, **kwargs):
        if not email:
            raise ValueError('Email must be provided!')
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_verified', True)
        
        superuser = self.model(
            email = self.normalize_email(email),
            **kwargs
        )
        superuser.set_password(password)
        superuser.save(using=self._db)
        return superuser
        


class User(AbstractUser):
    USER_ROLES = (
        ('viewer', 'Viewer'),
        ('operator', 'Operator')
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(db_index=True, unique=True, max_length=200, blank=False)
    is_verified = models.BooleanField(default=False)
    company_name = models.CharField(max_length=252, blank=True)
    role = models.CharField(max_length=100, choices=USER_ROLES)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    class Meta:
        unique_together = ['id', 'email']
    
    def assign_permissions(self):
        """
          Assign Permissions to User model
        """
        can_register_perm, _ = Permission.objects.get_or_create(codename='can_register_sensor')
        can_read_perm, _= Permission.objects.get_or_create(codename='can_read_sensor_detail')
        can_edit_sensor_perm, _ = Permission.objects.get_or_create(codename='can_edit_sensor_detail')
        can_delete_perm, _ = Permission.objects.get_or_create(codename='can_delete_sensor')
        
        self.user_permissions.add(can_register_perm)
        self.user_permissions.add(can_read_perm)
        self.user_permissions.add(can_edit_sensor_perm)
        self.user_permissions.add(can_delete_perm)
   
    def __str__(self) -> str:
        return self.email
        


# Sensor Information

class Sensor(models.Model):
    """
      Sensor Registration Model
    """
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Sensor Owner"), on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200, verbose_name=_('Sensor Name'), blank=True)
    description = models.TextField(blank=True)
    auth_credentials = models.BinaryField()
    location =  models.CharField(max_length=200, blank=True)
    data_format = models.CharField(max_length=100, blank=True)
    configuration = models.TextField(blank=True, verbose_name=_('Configuration on data handling process'))
    installation_date = models.DateTimeField(auto_now_add=True)
    communication_mode = models.CharField(max_length=150, blank=True)
    status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
       

    def __str__(self) -> str:
        if self.name:
            return self.name
        return self.id
    
    def update_last_active(self):
        current_time = timezone.now()
        if self.last_active != current_time:
            self.last_active = current_time
    
    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:
        self.update_last_active()
        return super().save(force_insert, force_update, using, update_fields)



class SensorData(models.Model):
    """ 
        Sensor data model for storing data from sensor
    """
    sensor = models.ForeignKey("Sensor", verbose_name=_("Sensor"), on_delete=models.CASCADE)
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    data = models.TextField()
    metadata = models.TextField(blank=True)
    data_type = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    unit_of_measurement = models.CharField(max_length=50, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return str(self.sensor)