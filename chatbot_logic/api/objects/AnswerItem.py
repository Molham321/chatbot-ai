class AnswerItem:
    """
    Represents a single bit of chatbot answer data which is grouped further to a AnswerSet.
    """
    question_id = 0
    question_text = ''
    answer_id = 0
    answer_text = ''
    answer_rating = 0.0

    def __init__(self, question_id, question_text, answer_id, answer_text, answer_rating):
        self.question_id = question_id
        self.question_text = question_text
        self.answer_id = answer_id
        self.answer_text = answer_text
        self.answer_rating = answer_rating

    def get_rating(self):
        return self.answer_rating