from django.db import models


class LegalPage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'legal'

    def __str__(self):
        return self.title