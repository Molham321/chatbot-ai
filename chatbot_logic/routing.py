import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path, path
from chatbot_logic.consumers.ChatRoomConsumer import ChatRoomConsumer
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fhe_chatbot.settings")

django_asgi_app = get_asgi_application()

websocket_urlpatterns = [
    re_path(
        r"ws/chat/(?P<session>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})/$", ChatRoomConsumer.as_asgi()
    ),
    path("ws/test/", ChatRoomConsumer.as_asgi())
]

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    }
)