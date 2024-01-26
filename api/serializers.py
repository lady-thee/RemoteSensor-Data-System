import re

# from django.core.exceptions import ValidationError
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

    def validate(self, data):
        password = data.get("password")
        validate_password(password)
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def get_user(self):
        request = self.context["request"]
        user = request.user
        return user

    def validate(self, data):
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        user = self.get_user()

        if not user.check_password(old_password):
            raise serializers.ValidationError("Password Incorrect!")

        try:
            validate_password(new_password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError("Password invalid!")

        return data

    def save(self, **kwargs):
        user = self.get_user()
        password = self.validated_data["new_password"]
        user.set_password(password)
        user.save()
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

    def get_user(self):
        request = self.context["request"]
        user = request.user
        return user

    def create(self, validated_data):
        user = self.get_user()
        sensor = Sensor.objects.create(operator=user, **validated_data)
        return sensor


class ProfileSettingsSerializer(serializers.ModelSerializer):
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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Account with Email does not exist!")

        if user and not user.check_password(password):
            raise serializers.ValidationError("Password is incorrect! Try again!")

        return data


class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        exclude = ("id", "sensor", "date_added")

    def get_sensor(self):
        request = self.context["request"]
        user = request.user
        sensor = Sensor.objects.get(operator=user)
        return sensor

    def create(self, validated_data):
        sensor = self.get_sensor()
        sensordata = SensorData.objects.create(sensor=sensor, **validated_data)
        return sensordata


class SensorSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        exclude = (
            "operator",
            "updated_at",
            "last_active",
        )


class SensorDataDetailsSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source="sensor.name", read_only=True)

    class Meta:
        model = SensorData
        exclude = ("sensor", "date_added")
