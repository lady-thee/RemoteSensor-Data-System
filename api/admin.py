from django.contrib import admin

from api.models import Sensor, SensorData, User


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "username",
        "company_name",
    ]

    list_display_links = ["email"]


admin.site.register(User, UserAdmin)


class SensorAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "operator",
        "description",
        "location",
        "data_format",
        "installation_date",
        "communication_mode",
        "status",
        "updated_at",
        "last_active",
    ]
    list_display_links = ["name", "operator"]


admin.site.register(Sensor, SensorAdmin)


class SensorDataAdmin(admin.ModelAdmin):
    list_display = [
        "sensor",
        "temperature",
        "humidity",
        "atmospheric_pressure",
        "wind_speed",
        "wind_direction",
        "rainfall",
        "weather_id",
        "main_weather",
        "weather_description",
        "temp_min",
        "temp_max",
        "sea_level_pressure",
        "ground_level_pressure",
        "wind_direction_deg",
        "wind_gust",
        "cloudiness_percentage",
        "visibility_distance",
        "city_id",
        "city_name",
        "http_response_code",
        "date_added",
    ]
    list_display_links = ["sensor"]


admin.site.register(SensorData, SensorDataAdmin)
