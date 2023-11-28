# Generated by Django 4.2.7 on 2023-11-11 14:54

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_alter_user_managers_alter_user_email"),
    ]

    operations = [
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
                ("auth_credentials", models.BinaryField()),
                ("location", models.CharField(blank=True, max_length=200)),
                ("data_format", models.CharField(blank=True, max_length=100)),
                (
                    "configuration",
                    models.TextField(
                        blank=True,
                        verbose_name="Configuration on data handling process",
                    ),
                ),
                ("installation_date", models.DateTimeField(auto_now_add=True)),
                ("communication_mode", models.CharField(blank=True, max_length=150)),
                ("status", models.BooleanField(default=True)),
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
        ),
    ]
