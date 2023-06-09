from django.db import models
from datetime import datetime


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
