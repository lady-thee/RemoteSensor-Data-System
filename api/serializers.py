import re

from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from api.models import Sensor, SensorData, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            "id",
            "is_active",
            "is_superuser",
            "is_verified",
            "is_staff",
            "date_joined",
            "last_login",
            "user_permissions",
            "groups",
        )

    def validate_email(self, email):
        pattern = "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

        if re.match(pattern, email):
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError("Email already exists!")
            return email
        else:
            raise serializers.ValidationError("Invalid Email format! Try again!")

    def create(self, validated_data):
        password = validated_data.get("password")
        role = validated_data.get("role")

        error_messages = []

        try:
            validate_password(password)
        except Exception as e:
            error_messages.append(str(e))

        if error_messages:
            raise serializers.ValidationError(error_messages)

        user = User.objects.create_user(**validated_data)

        return user


class SensorRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        exclude = (
            "id",
            "operator",
            "updated_at",
            "last_active",
        )
