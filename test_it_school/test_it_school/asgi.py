import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_it_school.settings')

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

try:
    from ws_app.routing import websocket_urlpatterns
    print(f"✅ WebSocket patterns loaded: {websocket_urlpatterns}")
except ImportError as e:
    print(f"❌ Error importing WebSocket routing: {e}")
    websocket_urlpatterns = []

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
