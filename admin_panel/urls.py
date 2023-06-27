"""admin_panel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from admin_panel import views

app_name = 'admin_panel'
urlpatterns = [
    path('', views.index_view, name='admin_index'),
    path('login/', views.login_view, name='admin_login'),
    path('login/login_user/', views.login_user_view, name='admin_login_user'),
    path('logout/', views.logout_user_view, name='admin_logout_user'),
    path('settings/', views.settings_view, name='admin_settings'),
    path('settings/save/', views.save_settings_view, name='admin_settings_save'),
    path('logging/', views.logging_view, name='admin_logging'),
    path('logging/download/', views.log_download_view, name='admin_logging_download'),
    path('logging/<log_id>/', views.logging_detail_view, name='admin_logging_detail'),
    path('questions/', views.questions_view, name='admin_questions'),

    path('chats/', views.chats_view, name='admin_chat'),
    path('chats/<chat_id>/', views.chat_detail_view, name='admin_chat_details'),
    path('chat/<str:session_token>/', views.chat_view, name='admin_chat_room'),

    path('questions/edit/<question_id>/', views.edit_questions_view, name='admin_questions_edit'),
    path('questions/edit/<question_id>/save/', views.save_questions_view, name='admin_questions_save'),
    path('questions/create/', views.create_questions_view, name='admin_questions_create'),
    path('questions/toggle/', views.toggle_questions_view, name='admin_questions_toggle'),

    path('answers/edit/<answer_id>/', views.edit_answers_view, name='admin_answers_edit'),
    path('answers/edit/<answer_id>/save/', views.save_answers_view, name='admin_answers_save'),
    path('answers/create/', views.create_answers_view, name='admin_answers_create'),

    path('contexts/edit/<context_id>/', views.edit_contexts_view, name='admin_contexts_edit'),
    path('contexts/edit/<context_id>/save/', views.save_contexts_view, name='admin_contexts_save'),
    path('contexts/create/', views.create_contexts_view, name='admin_contexts_create'),
]

