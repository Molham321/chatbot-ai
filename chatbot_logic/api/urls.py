from django.urls import path
from chatbot_logic.api.views import api_get_answer, api_get_chatbot, api_render_message

app_name = 'chatbot_logic'

urlpatterns = [
    path('question/', api_get_answer, name='api_question'),
    path('render_message/', api_render_message, name='api_answer'),
    path('', api_get_chatbot, name='api_chatbot')
]