from django.db import models
from datetime import datetime

# Create your models here.

class BotChat(models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    email = models.EmailField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Save a ConversationLog
        """
        super(BotChat, self).save(*args, **kwargs)

class ChatbotConversationLog (models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    asked_question = models.CharField(max_length=300)
    similarity_factor = models.FloatField(default=0.0)
    context_factor = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        """
        Save a ConversationLog
        """
        super(ChatbotConversationLog, self).save(*args, **kwargs)

    # Show the log date + the asked question instead of "ChatbotConversationLog_object" at the admin page
    def __str__(self):
        return str(self.created_at) + " - Asked question: " + self.asked_question
        
class CalculatedAnswer (models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True)
    answer = models.ForeignKey('chatbot_logic.Answer', on_delete=models.CASCADE, null=True)
    question = models.ForeignKey('chatbot_logic.Question', on_delete=models.CASCADE, null=True)
    chatbot_log = models.ForeignKey(ChatbotConversationLog, on_delete=models.SET_NULL, null=True)
    simularity = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        """
        Save a CalculatedAnswer
        """
        super(CalculatedAnswer, self).save(*args, **kwargs)

    def __str__(self):
        if self.answer:
            return "Answer: " + self.answer.answer_text + " | Similarity: " + str(self.simularity)

class ChatbotSoftwareLog (models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    executed_function = models.CharField(max_length=50)
    error_message = models.CharField(max_length=300)
    
    class LoggingLevel(models.IntegerChoices):
        DEBUG = 0
        INFO = 1
        WARN = 2
        ERROR = 3
        FATAL = 4

    logging_level = models.IntegerField(choices=LoggingLevel.choices, default=LoggingLevel.DEBUG)

    def save(self, *args, **kwargs):
        """
        Save a ConversationLog
        """
        super(ChatbotSoftwareLog, self).save(*args, **kwargs)