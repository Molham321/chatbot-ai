import spacy
from nltk import word_tokenize
from nltk.corpus import stopwords

from admin_panel.models import AdminSettings
from chatbot_logic.api.objects.AnswerItem import AnswerItem
from chatbot_logic.models import Question
from chatbot_logic.models import Context as ModelContext
from fhe_chatbot.classes.Singleton import Singleton


class CMatcher(metaclass=Singleton):

    def __init__(self):

        self.StopWords = stopwords.words("german")  # German Stopwords from the NLTK framework.
        self.DBEntries = self.LoadDBEntries()  # Method needs to be implemented.
        self.Context = ""  # Context of the last answer.
        self.NLP = spacy.load('de_core_news_md')  # Vector with semantic values for german words from spaCy.
        self.Settings = AdminSettings.objects.first()
        self.SimilarityFactor = self.LoadSimilarityFactor()
        self.ContextFactor = self.LoadContextFactor()

    # Returns the calculated cosine similarity between a String and a CDBEntry. The result is a value between 0 and 1.
    # A higher value means a higher similarity.
    # Parameters:
    # _Input: String (Question that the user entered on the frontend)
    # _DBEntry: CDBEntry (Question-Answer pair from the DB)
    def CosineSimilarity(self, _Input, _DBEntry):

        InputTokens = word_tokenize(_Input.lower())
        DBEntryTokens = word_tokenize(_DBEntry.lower())

        InputSet = {w for w in InputTokens if not w in self.StopWords}
        DBEntrySet = {w for w in DBEntryTokens if not w in self.StopWords}

        InputVector = []
        DBEntryVector = []
        UnionVector = InputSet.union(DBEntrySet)

        for w in UnionVector:

            if w in InputSet:
                InputVector.append(1)
            else:
                InputVector.append(0)

            if w in DBEntrySet:
                DBEntryVector.append(1)
            else:
                DBEntryVector.append(0)

        c = 0

        for i in range(UnionVector.__len__()):
            c += InputVector[i] * DBEntryVector[i]

        cosine = c / float((sum(InputVector) * sum(DBEntryVector)) ** 0.5)

        return cosine

    # Returns the calculated similarity between a String and a CDBEntry using the spaCy library. The result is a value
    # between 0 and 1. A higher value means a higher similarity.
    # Parameters:
    # _Input: String (Question that the user entered on the frontend)
    # _DBEntry: CDBEntry (Question-Answer pair from the DB)
    def SpacySimilarity(self, _Input, _DBEntry):

        InputTokens = word_tokenize(_Input)
        DBEntryTokens = word_tokenize(_DBEntry)

        InputSet = {w for w in InputTokens if not w in self.StopWords}
        DBEntrySet = {w for w in DBEntryTokens if not w in self.StopWords}

        Input_NLP = self.NLP(" ".join(InputSet))
        DBEntry_NLP = self.NLP(" ".join(DBEntrySet))

        Vector = []

        for w in Input_NLP:

            similarity = 0

            for x in DBEntry_NLP:

                if similarity < w.similarity(x):
                    similarity = w.similarity(x)

            Vector.append(similarity)

        return sum(Vector) / Vector.__len__()

    # Returns whether the context of the CMatcher instance and the given CDBEntry instance is similar. If the context is
    # similar, the result is 1, else the reuslt is 0.
    # Parameters:
    # _DBEntry: CDBEntry (Question-Answer pair from the DB)
    def ContextSimilar(self, _Context):

        Context = 0

        if self.Context == _Context:
            Context = 1

        return Context

    # TODO: Implement LoadDBEntries().
    # Returns a list of CDBEntry instances. The instances are generated from the Question-Answer pairs in the DB.
    def LoadDBEntries(self):
        return Question.objects.filter(active=True).all().select_related('answer')

    # TODO: Implement LoadSimilarityFactor().
    # Returns the SimilarityFactor, which gets defined in the administration frontend.
    def LoadSimilarityFactor(self):
        return float(self.Settings.similarity_factor)

    # TODO: Implement LoadContextFactor().
    # Returns the ContextFactor, which gets defined in the administration frontend.
    def LoadContextFactor(self):
        return float(self.Settings.context_factor)

    # Returns the calculated similarity value for a String and CDBEntry instance. The value of the results varies and
    # depends on the similarity between the given String, the given CDBEntry instance and the SimilarityFactor. This
    # value indicates, how similar the String and the CDBEntry instance are. A higher value is better.
    # Parameters:
    # _Input: String (Question that the user entered on the frontend)
    # _DBEntry: CDBEntry (Question-Answer pair from the DB)
    def SimilarityValue(self, _Input, _DBEntry):

        similarity = self.SpacySimilarity(_Input, _DBEntry.question_text)
        context_item = ModelContext.objects.filter(question=_DBEntry)

        if context_item.count() == 1:

            if similarity == 1:
                self.Context = context_item.first().context_text

        return similarity * self.SimilarityFactor

    # Returns an List of tuples {CDBEntry, MatchingValue}. The first part of a tuple is an CDBEntry instance and the
    # second part is a float. The MatchingValue is generated via the MatchingValue(...) method. The list contains a
    # tuple for each Question-Answer pair in the DB and is sorted descending on the MatchingValue. This means, that the
    # CDBEntry, which matches best with the given input String is in the first tuple in the list, the next best is  in
    # the second tuple and so forth.
    # The method also changes the value of the Context attribute of the CMatcher instance, if the similarity of a
    # CDBEntry instance and the given input String is 1.
    # Parameters:
    # _Input: String (Question that the user entered on the frontend)
    def MatchingList(self, _Input):

        answers = []

        for DBEntry in self.DBEntries:

            context_item = ModelContext.objects.filter(question=DBEntry)

            matching_value = self.SimilarityValue(_Input, DBEntry)

            if context_item.count() == 1:

                context_value = self.ContextSimilar(context_item.first().context_text) * self.ContextFactor
            else:

                context_value = 0

            answer = AnswerItem(
                question_id=DBEntry.id,
                question_text=DBEntry.question_text,
                answer_id=DBEntry.answer.id,
                answer_text=DBEntry.answer.answer_text,
                answer_rating=matching_value + context_value,
            )

            answers.append(answer)

        answers.sort(key=lambda x: x.get_rating(), reverse=True)

        return answers
