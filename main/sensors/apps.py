from django.apps import AppConfig


class SensorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sensors'

    def ready(self):
        import sensors.signals  # noqa to register signal handlers