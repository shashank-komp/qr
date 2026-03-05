from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    
    re_path(r'ws/transfer/(?P<session_id>\w+)/$', consumers.FileTransferConsumer.as_asgi()),
]