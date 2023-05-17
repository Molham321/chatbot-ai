from chatbot_logging.services.LoggingService import LoggingService
from chatbot_logic.api.objects.AnswerSet import AnswerSet
from chatbot_logic.classes.CMatcher import CMatcher


class MatchController:
    """
    Provides controller function for the chatbot matching algorithms.
    """
    logging_service: LoggingService = LoggingService()

    def match_against_db(self, question):
        """
        Matches the user question against all available registered question in the database.
        :param question: String containing the user question
        :return: List containing the top matched questions.
        """
        # Get the matching_list
        matcher = CMatcher()
        matching_list = matcher.MatchingList(question)

        # Log the matching_list
        # Nice to have: Outsource to thread for asynchronous logging (less response time)
        self.logging_service.save_conversation_log(question, matching_list)

        # Return Top answers
        answer_set = AnswerSet(matching_list[0], matching_list[1:4])
        return answer_set
