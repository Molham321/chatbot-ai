import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chatbot_logic.classes.ChatSessions import ChatSessions


@database_sync_to_async
def get_active_sessions():
    chat_sessions = ChatSessions()
    active_chats = chat_sessions.get_active_sessions()

    serialized_sessions = []

    for chat in active_chats:

        initial_message = ''
        if len(chat.first_chat_message) > 0:
            initial_message = chat.first_chat_message[0].message

        serialized_sessions.append({
            'id': chat.chat_session.id,
            'session_token': str(chat.chat_session.token),
            'created_at': str(chat.chat_session.created_at),
            'is_employee_present': chat.user is not None,
            'initial_message': initial_message
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
                    "session": {
                        "session_token": str(new_session.token),
                        "initial_message": event["initial_message"]
                    },
                    "user_id": event["user_id"]
                }
            )
        )

    async def chat_session_ended(self, event):
        session_token = event["session_token"]

        await self.send(
            text_data=json.dumps(
                {
                    "event": "chat_session_ended_notification",
                    "session_token": session_token,
                }
            )
        )

    async def employee_joined_chat(self, event):
        session_token = event["session_token"]

        await self.send(
            text_data=json.dumps(
                {
                    "event": "employee_joined_notification",
                    "session_token": session_token,
                }
            )
        )

    async def employee_left_chat(self, event):
        session_token = event["session_token"]

        await self.send(
            text_data=json.dumps(
                {
                    "event": "employee_left_notification",
                    "session_token": session_token,
                }
            )
        )
