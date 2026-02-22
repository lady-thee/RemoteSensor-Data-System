import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _



class SensorType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    fields = models.JSONField()
    fields_hash = models.CharField(max_length=255, blank=True)


class Sensor(models.Model):
    class SensorStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        DELETED = "DELETED", "Deleted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Sensor Owner"),
        on_delete=models.CASCADE,
        related_name="sensors",
    )

    name = models.CharField(max_length=200, verbose_name=_("Sensor Name"))
    description = models.TextField(blank=True)
    sensor_type = models.ForeignKey(
       SensorType, on_delete=models.CASCADE, help_text=_("Type of sensor e.g. temperature, humidity")
    )
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    data_format = models.CharField(
        max_length=100, blank=True, help_text=_("Expected data format, e.g. JSON, CSV")
    )
    communication_mode = models.CharField(
        max_length=150, blank=True, help_text=_("e.g. MQTT, HTTP, LoRa, NB-IoT")
    )

    storage_limit_gb = models.PositiveIntegerField(default=1)
    data_retention_days = models.PositiveIntegerField(default=30)

    status = models.CharField(
        max_length=20,
        db_index=True,
        choices=SensorStatus.choices,
        default=SensorStatus.ACTIVE,
    )
    

    last_active = models.DateTimeField(null=True, blank=True)
    installation_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = "Sensors"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} ({self.sensor_type or 'unspecified'})"

    def mark_active(self):
        self.last_active = timezone.now()
        self.status = self.SensorStatus.ACTIVE
        self.save(update_fields=["last_active", "status"])



class SensorCredentials(models.Model):
    sensor = models.OneToOneField(Sensor, on_delete=models.CASCADE)
    mqtt_key = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
        help_text=_("MQTT Key credential for this sensor"),
    )
    mqtt_username = models.CharField(max_length=255, blank=True)
    topics = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"Credentials for {self.sensor.name or self.sensor.id}"