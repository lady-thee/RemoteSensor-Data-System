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
        
        operator_group, _ = Group.objects.get_or_create(name='Operator')
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
    id = models.UUIDField(default=uuid.uuid4, primary_key=True,unique=True, editable=False)
    email = models.EmailField(db_index=True, unique=True, max_length=200, blank=False)
    is_verified = models.BooleanField(default=False)
    company_name = models.CharField(max_length=252, blank=True)
    first_name = None
    last_name = None
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    class Meta:
        unique_together = ["id", "email"]
    
       
    def __str__(self) -> str:
        return self.email
    
    


# Sensor Information. This section describes the models for the Sensor


class Sensor(models.Model):
    """
    Sensor Registration Model
    """
    STATUS = (
        ('active', 'Active'),
        ('passive', 'Passive'),
        ('pending', 'Pending')
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Sensor Owner"),
        on_delete=models.CASCADE,
    )
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200, verbose_name=_("Sensor Name"), blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    data_format = models.CharField(max_length=100, blank=True)
    installation_date = models.DateTimeField(auto_now_add=True)
    communication_mode = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, blank=True, default='active')
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)

    
    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = "Sensors"
        
        
    def __str__(self) -> str:
        if self.name:
            return self.name
        return self.id

    def update_last_active(self):
        current_time = timezone.now()
        if self.last_active != current_time:
            self.last_active = current_time

    def save(self, *args, **kwargs):
        if not self.pk:  
            self.update_last_active()
        super().save(*args, **kwargs)



class SensorData(models.Model):
    """
    Model to store  sensor data
    """
    sensor = models.ForeignKey("Sensor", verbose_name=_("Sensor"), on_delete=models.CASCADE)
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    atmospheric_pressure = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    wind_speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wind_direction = models.CharField(max_length=20, blank=True)
    rainfall = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    weather_id = models.IntegerField(default=0)
    main_weather = models.CharField(max_length=50, default='')
    weather_description = models.CharField(max_length=100, default='')
    temp_min = models.FloatField(default=0.00)
    temp_max = models.FloatField(default=0.00)
    sea_level_pressure = models.IntegerField(default=0)
    ground_level_pressure = models.IntegerField(default=0)
    wind_direction_deg = models.IntegerField(default=0)
    wind_gust = models.FloatField(default=0.00)
    cloudiness_percentage = models.IntegerField(default=0)
    visibility_distance = models.IntegerField(default=0)
    city_id = models.IntegerField(default=0)
    city_name = models.CharField(max_length=100, blank=True)
    http_response_code = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = "Sensor Data"

    def __str__(self):
        return f"{self.sensor.name} - Sensor Data"


