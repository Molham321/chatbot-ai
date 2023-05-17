from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from chatbot_logging.models import ChatbotConversationLog, CalculatedAnswer
from chatbot_logging.serializers import CalculatedAnswerSerializer, ChatbotConversationLogSerializer


# Create your views here.

# TODO Async view for logging: https://docs.djangoproject.com/en/3.1/topics/http/views/#async-views
# api_view and renderer_classes are needed to be able to use this view as trigger for the logging.
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def create_conversation_log_view(request):
    #---- TEST DATA ----
    asked_question_test = "Was geht?"
    # Calculated answers will be a dict with Answer objects and the calculated simularity.
    # Therefore we can use a test_dict with Answer_Object_ID: simularity
    calculated_answers_dict_test = {
        1: 0.9999,
        2: 0.8888,
        3: 0.7777,
    }
    #-------------------

    #---- Create ChatbotConversationLog ----
    # A serializer want's data as dictionary with it's model fields as keys
    conversation_log_data= {
        "asked_question": asked_question_test,
    }
    conversation_serializer = ChatbotConversationLogSerializer(data=conversation_log_data)
    
    # We always have to validate the data dictionary before saving it with the serializer
    if (conversation_serializer.is_valid()):
        new_log_object = conversation_serializer.save()
    #---------------------------------------
    
    #---- Create CalcutedAnswers ----
    for answer in calculated_answers_dict_test:
        calculated_answers_data = {
            "answer": answer,
            "chatbot_log": new_log_object.id,
            "simularity": calculated_answers_dict_test[answer],
        }
        calculated_answers_serializer = CalculatedAnswerSerializer(data=calculated_answers_data)
        if (calculated_answers_serializer.is_valid()):
            calculated_answers_serializer.save()
    #--------------------------------

    return Response('Log db entries created !')

@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def create_log_file_view(request):
    conversation_logs = ChatbotConversationLog.objects.all()
    json_representation = {}

    # Build a dict for json representation
    # key: value -> ConversationLog: CalculatedAnswersList
    for log in conversation_logs:
        dict_key = log.__str__()
        for calculated_answer in log.calculatedanswer_set.all():
            json_representation.setdefault(dict_key, []).append(calculated_answer.__str__())

    return Response(json_representation)