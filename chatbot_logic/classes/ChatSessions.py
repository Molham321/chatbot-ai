from fhe_chatbot.classes.Singleton import Singleton
from chatbot_logic.models import ChatSession, Chat, ChatMessage
from channels.db import database_sync_to_async
import uuid


class ChatSessions(metaclass=Singleton):

    def instantiate_session(self):
        chat_session = ChatSession()
        chat_session.token = uuid.uuid4()

        chat_session.save()

        return chat_session

    def get_session(self, token, allow_closed = False):
        chat_session = ChatSession.objects.get(token=token)

        if chat_session is None:
            return None

        if not allow_closed and not chat_session.active:
            return None

        return chat_session
   

    @database_sync_to_async
    def instantiate_chat(self, session):
        try:
            existing_chat = Chat.objects.get(chat_session=session.id)
            return existing_chat
        except Chat.DoesNotExist:
            chat = Chat()
            chat.chat_session = session

            chat.save()

            return chat

    @database_sync_to_async
    def store_message(self, chat, message, from_guest=True, user=None):
        chat_message = ChatMessage()
        
        chat_message.chat = chat
        chat_message.user = user
        chat_message.message = message
        chat_message.from_guest = from_guest

        chat_message.save()
