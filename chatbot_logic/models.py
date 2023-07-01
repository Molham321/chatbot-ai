from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


# Create your models here.

class Answer(models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True)
    answer_text = models.CharField(max_length=600)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Save an Answer
        """
        super(Answer, self).save(*args, **kwargs)

    def __str__(self):
        return self.answer_text

    class Meta:
        ordering = ['answer_text']


class Context(models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True)
    context_text = models.CharField(max_length=80)

    def save(self, *args, **kwargs):
        """
        Save a Context
        """
        super(Context, self).save(*args, **kwargs)

    def __str__(self):
        return self.context_text

    class Meta:
        ordering = ['context_text']


class Question(models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True)
    answer = models.ForeignKey(Answer, null=True, on_delete=models.SET_NULL)
    context = models.ForeignKey(Context, null=True, on_delete=models.SET_NULL)
    question_text = models.CharField(max_length=300)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Save a Question
        """
        super(Question, self).save(*args, **kwargs)

    # Show the question instead of "question_object" at the admin page
    def __str__(self):
        return self.question_text

    class Meta:
        ordering = ['question_text']


class Keyword(models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True)
    question = models.ManyToManyField(Question)
    keyword_text = models.CharField(max_length=30)

    def save(self, *args, **kwargs):
        """
        Save a Keyword
        """
        super(Keyword, self).save(*args, **kwargs)

    def __str__(self):
        return self.keyword_text

    class Meta:
        ordering = ['keyword_text']


class Settings(models.Model):
    MATCHING_METHODS = [
        ('cosine', 'Cosine Matching'),
        ('spacy', 'Spacy Matching'),
    ]

    modified_at = models.DateTimeField(auto_now=True, blank=True)
    similarity_factor = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
    context_factor = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
    matching_method = models.CharField(max_length=6, choices=MATCHING_METHODS, default='cosine')

    def save(self, *args, **kwargs):
        """
        Save a Keyword
        """
        super(Settings, self).save(*args, **kwargs)

    def __str__(self):
        return "Chatbot Settings"

    class Meta:
        verbose_name_plural = "Settings"


class ChatSession(models.Model):
    token = models.UUIDField()
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "Chat Session"

    class Meta:
        verbose_name_plural = "Chat Sessions"


class Chat(models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True)
    chat_session = models.ForeignKey(ChatSession, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """
        Save a Chat
        """
        super(Chat, self).save(*args, **kwargs)

    def __str__(self):
        return "Chat"

    class Meta:
        verbose_name_plural = "Chats"


class EmailSupport(models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    chat_session = models.ForeignKey(ChatSession, null=True, on_delete=models.CASCADE)
    email = models.EmailField()

    def save(self, *args, **kwargs):
        """
        Save a Email support
        """
        super(EmailSupport, self).save(*args, **kwargs)


class ChatMessage(models.Model):
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    modifier_at = models.DateTimeField(auto_now=True, blank=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message = models.CharField(max_length=600)
    from_guest = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Save a Chat message
        """
        super(ChatMessage, self).save(*args, **kwargs)

    def __str__(self):
        return "Chat Message"

    class Meta:
        verbose_name_plural = "Chat Messages"
