from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('broker', 'Broker'),
        ('buyer', 'Buyer'),
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    agree_terms = models.BooleanField(default=False)
    terms_accepted_date = models.DateTimeField(
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.user_type})"

    @property
    def properties(self):
        return self.property_set.all()

    @property
    def properties_count(self):
        return self.properties.count()
