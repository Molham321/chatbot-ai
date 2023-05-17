from django.contrib import admin

from .models import ChatbotConversationLog, ChatbotSoftwareLog, CalculatedAnswer

# Register your models here.
admin.site.register(ChatbotConversationLog)
admin.site.register(ChatbotSoftwareLog)
admin.site.register(CalculatedAnswer)
