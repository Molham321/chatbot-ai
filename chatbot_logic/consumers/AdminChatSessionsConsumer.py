import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chatbot_logic.classes.ChatSessions import ChatSessions


@database_sync_to_async
def get_active_sessions():
    chat_sessions = ChatSessions()
    active_sessions = chat_sessions.get_active_sessions()

    serialized_sessions = []

    for session in active_sessions:
        serialized_sessions.append({
            'id': session.id,
            'session_token': str(session.token),
            'created_at': str(session.created_at)
        })

    return serialized_sessions


@database_sync_to_async
def get_new_chat_session(token):
    chat_sessions = ChatSessions()
    session = chat_sessions.get_session(token)
    return session


class AdminChatOverviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        if self.scope["user"].is_anonymous:
            await self.close()
            return
        else:
            await self.accept()

            await self.channel_layer.group_add("admin_group", self.channel_name)

            active_sessions = await get_active_sessions()

            await self.send(
                text_data=json.dumps(
                    {
                        "event": "active_sessions",
                        "sessions": active_sessions
                    }
                )
            )

    async def disconnect(self, code):
        await self.channel_layer.group_discard("admin_group", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if data["event"] == "new_chat_session":
            session_token = data["session_token"]
            new_session = await get_new_chat_session(session_token)

            await self.send(
                text_data=json.dumps(
                    {
                        "event": "new_chat_session_notification",
                        "session_token": session_token,
                    }
                )
            )

    async def new_chat_session(self, event):
        session_token = event["session_token"]
        new_session = await get_new_chat_session(session_token)

        await self.send(
            text_data=json.dumps(
                {
                    "event": "new_chat_session_notification",
                    "session_token": session_token,
                    "user_id": event["user_id"]
                }
            )
        )
