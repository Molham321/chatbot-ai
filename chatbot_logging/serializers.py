from rest_framework import serializers
from chatbot_logging.models import ChatbotConversationLog, CalculatedAnswer, ChatbotSoftwareLog


class ChatbotConversationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotConversationLog
        fields = ['id', 'asked_question']

class CalculatedAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculatedAnswer
        fields = ['id', 'answer', 'chatbot_log', 'simularity']

class ChatbotSoftwareLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotSoftwareLog
        fields = ['id', 'executed_function', 'error_message', 'logging_level']