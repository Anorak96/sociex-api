import os
from channels.routing import ProtocolTypeRouter, URLRouter
from Sociex.routing import websocket_pattern
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sociex.settings')

http_response_app = get_asgi_application()

application =ProtocolTypeRouter({
    "http": http_response_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_pattern
        )
    )
})