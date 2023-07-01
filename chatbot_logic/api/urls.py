from django.urls import path
from chatbot_logic.api.views import api_get_answer, api_get_chatbot, api_render_message, api_instantiate_session, api_send_email

app_name = 'chatbot_logic'

urlpatterns = [
    path('question/', api_get_answer, name='api_question'),
    path('render_message/', api_render_message, name='api_answer'),
    path('instantiate_session/', api_instantiate_session, name='api_instantiate_session'),
    path('email/', api_send_email, name='api_email'),
    path('', api_get_chatbot, name='api_chatbot')
]
