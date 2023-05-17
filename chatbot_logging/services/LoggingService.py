from admin_panel.models import AdminSettings
from chatbot_logging.models import CalculatedAnswer, ChatbotConversationLog
from fhe_chatbot.classes.Singleton import Singleton


class LoggingService(metaclass=Singleton):
    """
    Respresents a Service which handles all chatbot logging operations.
    Note that this class is implemented as a Singleton to prevent long loading times in the chatbot answer process.
    """
    def save_conversation_log(self, asked_question, matching_list):
        """
        Saves a conversation log to the database.
        :param asked_question: The question the user asked the chatbot.
        :param matching_list: A List with calculated similarities for all registered questions.
        """
        settings = AdminSettings.objects.first()
        conversation_log = ChatbotConversationLog()
        conversation_log.asked_question = asked_question
        conversation_log.context_factor = settings.context_factor
        conversation_log.similarity_factor = settings.similarity_factor
        conversation_log.save()

        for match in matching_list:
            self.save_answer(conversation_log, match)

    def save_answer(self, conversation_log, match):
        """
        Saves a single Match entry for the conversation log.
        :param conversation_log: The associated conversation log object.
        :param match: Object containing the matched data.
        """
        calculated_answer = CalculatedAnswer()
        calculated_answer.answer_id = match.answer_id
        calculated_answer.question_id = match.question_id
        calculated_answer.chatbot_log_id = conversation_log.id
        calculated_answer.simularity = match.answer_rating
        calculated_answer.save()
