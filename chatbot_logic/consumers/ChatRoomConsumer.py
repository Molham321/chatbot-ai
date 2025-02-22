import json
import asyncio

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from admin_panel.models import AdminSettings
from chatbot_logic.api.serializers import AnswerSetSerializer
from chatbot_logic.classes.ChatSessions import ChatSessions
from chatbot_logic.classes.EmailService import EmailService
from chatbot_logic.controllers.MatchController import MatchController

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


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
            noanswer_text='',
            employee_joined_text='',
            employee_left_text='',
            user_left_text='',

        )
        return settings


class ChatRoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.match_controller = None
        self.chat_sessions = None
        self.settings = None
        self.session_token = None
        self.chat_session = None
        self.chat = None
        self.user = None
        self.is_private = False
        self.is_interrupted = False

        self.email_state = None

    async def connect(self):
        self.session_token = self.scope["url_route"]["kwargs"]["session"]

        if self.scope["path"].startswith('/ws/admin/chat/'):
            self.is_private = True

        self.chat_sessions = ChatSessions()

        chat_session = await self.retrieve_session(self.session_token)

        if chat_session is None:
            await self.close()
            return
        else:
            self.chat_session = chat_session
            self.settings = await get_settings()
            self.match_controller = MatchController()

            await self.channel_layer.group_add(self.session_token, self.channel_name)

            await self.accept()

            if self.scope["user"].is_authenticated and self.is_private:
                self.user = self.scope["user"]

            if self.user is not None:

                self.chat = await self.get_chat()
                if self.chat.user is not None:
                    await self.close()
                    return

                await self.channel_layer.group_send(
                    self.session_token,
                    {
                        "type": "employee_joined_message",
                        "user": self.user
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
                chat.user = self.user
                await self.chat_sessions.store_chat(chat)

                await self.send_previous_chat()

            if self.user is None:
                await self.send_greeting_message()

    async def disconnect(self, code):

        has_guest_left = self.user is None

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

        if 'service_message' in text_data_json:
            await self.resolve_received_service_message(text_data_json)
            return

        await self.resolve_received_text_message(text_data_json)

    async def resolve_received_service_message(self, text_data_json):
        if text_data_json["service_message"] == "typing":
            print("Someone is typing...")

            await self.channel_layer.group_send(
                self.session_token,
                {
                    "type": "forward_typing_state",
                    "is_typing": text_data_json["is_typing"] == True,
                    "sender": "employee" if self.user is not None else "user",
                    "sender_channel_name": self.channel_name
                }
            )
        if text_data_json["service_message"] == "send_mail":
            print("Someone wants to send a mail...")

            await self.send_mail_request_message()

    async def resolve_received_text_message(self, text_data_json):
        message = text_data_json["message"]

        if "sender" in text_data_json and (text_data_json["sender"] == "bot"):
            return

        is_new_chat = False
        if self.chat is None:
            is_new_chat = True

        chat = await self.get_chat()
        user = self.user
        is_guest_message = True if user is None else False

        if self.email_state is None:
            await self.chat_sessions.store_message(chat, message, is_guest_message, user)

        if is_new_chat:
            await self.channel_layer.group_send(
                "admin_group",
                {
                    "type": "new_chat_session",
                    "session_token": self.session_token,
                    "initial_message": message,
                    "user_id": self.user.id if self.user is not None else None
                }
            )

        await self.channel_layer.group_send(
            self.session_token,
            {
                "type": "forward_message",
                "message": message,
                "sender": "employee" if self.user is not None else "user",
                "sender_channel_name": self.channel_name
            }
        )

        if self.chat.user is not None:
            return

        if self.email_state is None:
            await self.channel_layer.group_send(
                self.session_token,
                {
                    "type": "ask_question",
                    "question": message
                }
            )
        else:
            await self.channel_layer.group_send(
                self.session_token,
                {
                    "type": "handle_email",
                    "message": message
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

    async def forward_typing_state(self, event):
        is_typing = event["is_typing"]
        sender = event["sender"]
        sender_channel_name = event["sender_channel_name"]

        if self.channel_name != sender_channel_name:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "typing_state_changed",
                        "sender": sender,
                        "is_typing": is_typing
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

    async def send_mail_request_message(self):
        self.email_state = "request"

        await self.send(
            text_data=json.dumps(
                {
                    "sender": "bot",
                    "message": self.settings.mail_request_text,
                    "type": "reply",
                    "answer": {
                        "answer": self.settings.mail_request_text,
                        "assumed_answers": [
                            {
                                "question_text": "Ja"
                            },
                            {
                                "question_text": "Nein"
                            }
                        ]
                    }
                }
            )
        )

    async def send_previous_chat(self):
        chat_messages = await self.get_chat_messages()
        chat_history = []

        for message in chat_messages:

            sender = ''
            if message.from_guest:
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

        self.is_interrupted = True

        await self.send(
            text_data=json.dumps(
                {
                    "type": "employee_joined",
                    "sender": "system",
                    "message": self.settings.employee_joined_text
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
                    "message": self.settings.employee_left_text
                }
            )
        )

    async def guest_disconnected(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "guest_disconnected",
                    "sender": "system",
                    "message": self.settings.user_left_text
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

    async def refresh_chat(self):
        self.chat = await self.chat_sessions.instantiate_chat(self.chat_session)

    async def get_chat_messages(self):
        chat = await self.chat_sessions.get_chat_messages_from_active_session(session=self.chat_session)
        return chat

    async def ask_question(self, event):
        question = event["question"]

        self.is_interrupted = False

        await self.send(
            text_data=json.dumps(
                {
                    "sender": "bot",
                    "type": "loading",
                    "message": None
                }
            )
        )

        await asyncio.sleep(2)

        await self.refresh_chat()

        if self.chat.user is not None:
            return

        answer = await self.match_question(question)
        serializer = AnswerSetSerializer(answer)

        await self.refresh_chat()

        if self.chat.user is not None:
            return

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

    async def handle_email(self, event):
        message = event["message"]

        await asyncio.sleep(1)

        if self.email_state == "request":

            if message == "Ja":
                self.email_state = "input"

                await self.send(
                    text_data=json.dumps(
                        {
                            "sender": "bot",
                            "type": "reply",
                            "mail_state": "input",
                            "message": self.settings.mail_input_text
                        }
                    )
                )
            else:
                self.email_state = None

                await self.send(
                    text_data=json.dumps(
                        {
                            "sender": "bot",
                            "type": "reply",
                            "mail_state": None,
                            "message": self.settings.mail_cancel_text
                        }
                    )
                )

        elif self.email_state == "input":
            try:
                validate_email(message)

                await self.send_email(message)

                self.email_state = None

                await self.send(
                    text_data=json.dumps(
                        {
                            "sender": "bot",
                            "type": "reply",
                            "mail_state": "submitted",
                            "message": self.settings.mail_sent_text
                        }
                    )
                )
            except ValidationError as e:
                await self.send(
                    text_data=json.dumps(
                        {
                            "sender": "bot",
                            "type": "reply",
                            "mail_state": "input",
                            "message": self.settings.mail_invalid_input_text
                        }
                    )
                )

    @sync_to_async
    def send_email(self, recipient):
        email_service = EmailService()

        print("asdf")

        email_service.send_email(self.chat_session, recipient)