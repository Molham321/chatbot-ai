from django.urls import path
from chatbot_logging.views import create_conversation_log_view, create_log_file_view

app_name = 'chatbot_logging'

urlpatterns = [
    path('test/', create_conversation_log_view, name='logging'),
    path('logfile/', create_log_file_view, name='logging'),
]