import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.qr import routing 
from tools_box.config.settings import CoreConfigReader
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CoreConfigReader(file_path=str(BASE_DIR / ".env"))


os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'core.settings.{CoreConfigReader.get_config("ENVIRONMENT", default="local")}')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        routing.websocket_urlpatterns
    ),
})