import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from admin_panel.models import AdminSettings
from chatbot_logic.controllers.MatchController import MatchController
from chatbot_logic.classes.ChatSessions import ChatSessions
from chatbot_logic.api.serializers import AnswerSetSerializer
from channels.db import database_sync_to_async


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
        self.match_controller = None
        self.chat_sessions = None
        self.settings = None
        self.session = None

    async def connect(self):
        self.session = self.scope["url_route"]["kwargs"]["session"]

        self.chat_sessions = ChatSessions()

        chat_session = self.retrieve_session(self.session)

        if chat_session is None:
            await self.close()
        else:
            self.settings = await get_settings()
            self.match_controller = MatchController()

            await self.channel_layer.group_add(self.session, self.channel_name)

            await self.accept()

            await self.channel_layer.group_send(
                self.session,
                {
                    "type": "greeting_message"
                }
            )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.session, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        message = text_data_json["message"]

        if "sender" in text_data_json and text_data_json["sender"] == "bot":
            return

        await self.channel_layer.group_send(
            self.session,
            {
                "type": "ask_question",
                "question": message
            }
        )

    async def greeting_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "sender": "bot",
                    "message": self.settings.greeting_text
                }
            )
        )

    @sync_to_async
    def match_question(self, question):
        return self.match_controller.match_against_db(question)

    @sync_to_async
    def retrieve_session(self, token):
        return self.chat_sessions.get_session(token)

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
