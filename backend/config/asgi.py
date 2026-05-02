import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from apps.realtime.middleware import JWTAuthMiddleware
from apps.realtime.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
