import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from django.urls import path

from api.consumers import SensorConsumer

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        path("wss/", SensorConsumer.as_asgi()),
                        path("wss/data/", SensorConsumer.as_asgi()),
                    ]
                )
            ),
            # ["https://sensorfusionweather.onrender.com", "127.0.0.1:5500"],
        ),
    }
)
