import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path, path

from chatbot_logic.consumers.AdminChatSessionsConsumer import AdminChatOverviewConsumer
from chatbot_logic.consumers.ChatRoomConsumer import ChatRoomConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fhe_chatbot.settings")

django_asgi_app = get_asgi_application()

websocket_urlpatterns = [
    re_path(
        r"ws/chat/(?P<session>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})/$",
        ChatRoomConsumer.as_asgi()
    ),
    re_path("ws/admin/chats/", AdminChatOverviewConsumer.as_asgi()),
    re_path(r"ws/admin/chat/(?P<session>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})/$",
            ChatRoomConsumer.as_asgi()),
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
