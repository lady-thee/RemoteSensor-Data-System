# Generated by Django 5.0.1 on 2024-01-27 13:48

import uuid

import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "email",
                    models.EmailField(db_index=True, max_length=200, unique=True),
                ),
                ("is_verified", models.BooleanField(default=False)),
                ("company_name", models.CharField(blank=True, max_length=252)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "unique_together": {("id", "email")},
            },
        ),
        migrations.CreateModel(
            name="Sensor",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Sensor Name"
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("location", models.CharField(blank=True, max_length=200)),
                ("data_format", models.CharField(blank=True, max_length=100)),
                ("installation_date", models.DateTimeField(auto_now_add=True)),
                ("communication_mode", models.CharField(blank=True, max_length=150)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("active", "Active"),
                            ("passive", "Passive"),
                            ("pending", "Pending"),
                        ],
                        default="active",
                        max_length=10,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_active", models.DateTimeField(auto_now=True)),
                (
                    "operator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Sensor Owner",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sensor",
                "verbose_name_plural": "Sensors",
            },
        ),
        migrations.CreateModel(
            name="SensorData",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "temperature",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                (
                    "humidity",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                (
                    "atmospheric_pressure",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=7, null=True
                    ),
                ),
                (
                    "wind_speed",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=6, null=True
                    ),
                ),
                ("wind_direction", models.CharField(blank=True, max_length=20)),
                (
                    "rainfall",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=6, null=True
                    ),
                ),
                ("weather_id", models.IntegerField(default=0)),
                ("main_weather", models.CharField(default="", max_length=50)),
                ("weather_description", models.CharField(default="", max_length=100)),
                ("temp_min", models.FloatField(default=0.0)),
                ("temp_max", models.FloatField(default=0.0)),
                ("sea_level_pressure", models.IntegerField(default=0)),
                ("ground_level_pressure", models.IntegerField(default=0)),
                ("wind_direction_deg", models.IntegerField(default=0)),
                ("wind_gust", models.FloatField(default=0.0)),
                ("cloudiness_percentage", models.IntegerField(default=0)),
                ("visibility_distance", models.IntegerField(default=0)),
                ("city_id", models.IntegerField(default=0)),
                ("city_name", models.CharField(blank=True, max_length=100)),
                ("http_response_code", models.IntegerField(default=0)),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "sensor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.sensor",
                        verbose_name="Sensor",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Sensor Data",
            },
        ),
    ]
