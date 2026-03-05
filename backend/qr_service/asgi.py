import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import qr.routing # Update this

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_service.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            qr.routing.websocket_urlpatterns
        )
    ),
})