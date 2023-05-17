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

        def save(self, *args, **kwargs):
            """
            Save a Keyword
            """
            super(AdminSettings, self).save(*args, **kwargs)

        def __str__(self):
            return "AdminSettings"

        class Meta:
            verbose_name_plural = "AdminSettings"