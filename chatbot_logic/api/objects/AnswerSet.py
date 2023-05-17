from chatbot_logic.api.objects.AnswerItem import AnswerItem


class AnswerSet:
    """
    Represents a chatbot answer, containing the top answer and a number of assumed questions / answers.
    """
    answer = AnswerItem(0, "", 0, "", 0.0)
    assumed_answers = []

    def __init__(self, answer, assumed_answers):
        self.answer = answer
        self.assumed_answers = assumed_answers
