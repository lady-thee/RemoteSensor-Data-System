
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

from api.consumers import SensorConsumer



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_aspi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": django_aspi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/data/", SensorConsumer.as_asgi()),
                    path("ws/", SensorConsumer.as_asgi()),
                    
                ]
            )
        ),
    ),
})
