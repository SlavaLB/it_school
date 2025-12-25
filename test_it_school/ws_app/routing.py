from django.urls import re_path
from ws_app import consumers

websocket_urlpatterns = [
    re_path(r'ws/lesson/$', consumers.SimpleConsumer.as_asgi()),
]
