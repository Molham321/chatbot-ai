from fhe_chatbot.classes.Singleton import Singleton
from chatbot_logic.models import ChatSession
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
