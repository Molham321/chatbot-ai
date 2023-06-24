import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from admin_panel.models import AdminSettings
from chatbot_logic.api.serializers import AnswerSetSerializer
from chatbot_logic.classes.ChatSessions import ChatSessions
from chatbot_logic.controllers.MatchController import MatchController


@database_sync_to_async
def get_settings():
    count = AdminSettings.objects.count()

    if count == 1:
        return AdminSettings.objects.first()
    else:
        settings = AdminSettings.objects.create(
            similarity_factor=1.0,
            context_factor=1.0,
            matching_method='cosine',
            greeting_text='',
            noanswer_text=''
        )
        return settings


class ChatRoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        print("Tehest")
        self.match_controller = None
        self.chat_sessions = None
        self.settings = None
        self.session_token = None
        self.chat_session = None
        self.chat = None

    async def connect(self):
        self.session_token = self.scope["url_route"]["kwargs"]["session"]

        self.chat_sessions = ChatSessions()

        chat_session = await self.retrieve_session(self.session_token)

        print(chat_session)

        if chat_session is None:
            await self.close()
            return
        else:
            self.chat_session = chat_session
            self.settings = await get_settings()
            self.match_controller = MatchController()

            await self.channel_layer.group_add(self.session_token, self.channel_name)

            await self.accept()

            if self.scope["user"].is_authenticated:
                await self.channel_layer.group_send(
                    self.session_token,
                    {
                        "type": "employee_joined_message",
                        "user": self.scope["user"]
                    }
                )

                await self.channel_layer.group_send(
                    "admin_group",
                    {
                        "type": "employee_joined_chat",
                        "session_token": self.session_token
                    }
                )

                chat = await self.get_chat()
                chat.user = self.scope["user"]
                await self.chat_sessions.store_chat(chat)

                await self.send_previous_chat()

            if not self.scope["user"].is_authenticated:
                await self.send_greeting_message()

    async def disconnect(self, code):

        has_guest_left = not self.scope["user"].is_authenticated

        if has_guest_left:
            await self.chat_sessions.set_chatsession_inactive(self.chat_session)

            await self.channel_layer.group_send(
                self.session_token,
                {
                    "type": "guest_disconnected"
                }
            )

        if not has_guest_left:
            chat = await self.get_chat()
            chat.user = None
            await ChatSessions.store_chat(chat)

            await self.channel_layer.group_send(
                self.session_token,
                {
                    "type": "employee_left_message"
                }
            )

            await self.channel_layer.group_send(
                "admin_group",
                {
                    "type": "employee_left_chat",
                    "session_token": self.session_token,
                }
            )

        else:

            await self.channel_layer.group_send(
                "admin_group",
                {
                    "type": "chat_session_ended",
                    "session_token": self.session_token,
                }
            )

        await self.channel_layer.group_discard(self.session_token, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        message = text_data_json["message"]

        if "sender" in text_data_json and (text_data_json["sender"] == "bot"):
            return

        is_new_chat = False
        if self.chat is None:
            is_new_chat = True

        chat = await self.get_chat()
        user = self.scope["user"] if self.scope["user"].is_authenticated else None
        is_guest_message = True if user is None else False

        await self.chat_sessions.store_message(chat, message, is_guest_message, user)

        if is_new_chat:
            await self.channel_layer.group_send(
                "admin_group",
                {
                    "type": "new_chat_session",
                    "session_token": self.session_token,
                    "initial_message": message,
                    "user_id": self.scope["user"].id if self.scope["user"].is_authenticated else None
                }
            )

        await self.channel_layer.group_send(
            self.session_token,
            {
                "type": "forward_message",
                "message": message,
                "sender": "employee" if self.scope["user"].is_authenticated else "user",
                "sender_channel_name": self.channel_name
            }
        )

        if self.chat.user is not None:
            return

        await self.channel_layer.group_send(
            self.session_token,
            {
                "type": "ask_question",
                "question": message
            }
        )

    async def forward_message(self, event):
        message = event["message"]
        sender = event["sender"]
        sender_channel_name = event["sender_channel_name"]

        if self.channel_name != sender_channel_name:
            await self.send(
                text_data=json.dumps(
                    {
                        "sender": sender,
                        "message": message
                    }
                )
            )

    async def send_greeting_message(self):
        await self.send(
            text_data=json.dumps(
                {
                    "sender": "bot",
                    "message": self.settings.greeting_text
                }
            )
        )

    async def send_previous_chat(self):
        chat_messages = await self.get_chat_messages()
        chat_history = []

        for message in chat_messages:

            sender = ''
            if message.from_guest == True:
                sender = 'user'
            elif message.user is None:
                sender = 'bot'
            elif message.user is not None:
                sender = 'employee'

            chat_history.append({
                'id': message.id,
                'created_at': str(message.created_at),
                'message': message.message,
                'sender': sender
            })

        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat_history",
                    "sender": "system",
                    "messages": chat_history
                }
            )
        )

    async def employee_joined_message(self, event):

        await self.get_chat()
        self.chat.user = event["user"]

        await self.send(
            text_data=json.dumps(
                {
                    "type": "employee_joined",
                    "sender": "system",
                    # TODO: Add to configurations in admin panel
                    "message": "Ein Mitarbeiter ist der Unterhaltung beigetreten."
                }
            )
        )

    async def employee_left_message(self, event):
        await self.get_chat()
        self.chat.user = None

        await self.send(
            text_data=json.dumps(
                {
                    "type": "employee_disconnected",
                    "sender": "system",
                    # TODO: Add to configurations in admin panel
                    "message": "Der Mitarbeiter hat die Unterhaltung verlassen."
                }
            )
        )

    async def guest_disconnected(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "guest_disconnected",
                    "sender": "system",
                    "message": "Der Nutzer hat die Unterhaltung verlassen."
                }
            )
        )

    @sync_to_async
    def match_question(self, question):
        return self.match_controller.match_against_db(question)

    @sync_to_async
    def retrieve_session(self, token):
        return self.chat_sessions.get_session(token)

    async def get_chat(self):
        if self.chat is None:
            self.chat = await self.chat_sessions.instantiate_chat(self.chat_session)

        return self.chat

    async def get_chat_messages(self):
        chat = await self.chat_sessions.get_chat_messages_from_active_session(session=self.chat_session)
        return chat

    async def ask_question(self, event):
        question = event["question"]

        await self.send(
            text_data=json.dumps(
                {
                    "sender": "bot",
                    "type": "loading",
                    "message": None
                }
            )
        )

        answer = await self.match_question(question)
        serializer = AnswerSetSerializer(answer)

        message = answer.answer.answer_text

        chat = await self.get_chat()
        await self.chat_sessions.store_message(chat, message, False)

        await self.send(
            text_data=json.dumps(
                {
                    "sender": "bot",
                    "type": "reply",
                    "message": message,
                    "answer": serializer.data
                }
            )
        )

#    async def instantiate_chat(self, chat_session):
#        existing_chat =
