from django.db import models

# Create your models here.


class AdminSettings(models.Model):
        MATCHING_METHODS = [
            ('cosine', 'Cosine Matching'),
            ('spacy', 'Spacy Matching'),
        ]

        modified_at = models.DateTimeField(auto_now=True, blank=True)
        similarity_factor = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
        context_factor = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
        matching_method = models.CharField(max_length=6, choices=MATCHING_METHODS, default='cosine')
        greeting_text = models.CharField(max_length=255)
        noanswer_text = models.CharField(max_length=255)
        employee_joined_text = models.CharField(max_length=255)
        employee_left_text = models.CharField(max_length=255)
        user_left_text=models.CharField(max_length=255)
        mail_timeout_in_seconds = models.IntegerField(default=600)
        similarity_mail_threshold = models.FloatField(default=0.2)
        number_of_quality_test_answers = models.IntegerField(default=5)

        def save(self, *args, **kwargs):
            """
            Save a Keyword
            """
            super(AdminSettings, self).save(*args, **kwargs)

        def __str__(self):
            return "AdminSettings"

        class Meta:
            verbose_name_plural = "AdminSettings"