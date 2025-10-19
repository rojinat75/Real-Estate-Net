from django.db import models
from django.conf import settings
from properties.models import Property
from django.utils import timezone

class PageView(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='page_views', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.URLField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    referrer = models.URLField(blank=True, null=True)
    time_spent = models.IntegerField(default=0)  # in seconds

    def __str__(self):
        return f"{self.url or self.property.title if self.property else 'Unknown'} viewed by {self.user.username if self.user else 'Anonymous'} at {self.timestamp}"

class UserActivity(models.Model):
    ACTIVITY_CHOICES = (
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('property_view', 'Property Viewed'),
        ('property_create', 'Property Created'),
        ('property_update', 'Property Updated'),
        ('property_delete', 'Property Deleted'),
        ('search', 'Property Search'),
        ('contact', 'Contact Form Submitted'),
        ('premium_purchase', 'Premium Purchase'),
        ('profile_update', 'Profile Updated'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)  # For additional data

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"

class TrafficAnalytics(models.Model):
    date = models.DateField(default=timezone.now)
    total_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    page_views = models.IntegerField(default=0)
    bounce_rate = models.FloatField(default=0.0)
    avg_session_duration = models.IntegerField(default=0)  # in seconds

    class Meta:
        unique_together = ('date',)

    def __str__(self):
        return f"Traffic Analytics for {self.date}"

class PropertyAnalytics(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='analytics')
    total_views = models.IntegerField(default=0)
    unique_viewers = models.IntegerField(default=0)
    avg_time_on_page = models.IntegerField(default=0)  # in seconds
    inquiry_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Analytics for {self.property.title}"

class RevenueAnalytics(models.Model):
    date = models.DateField(default=timezone.now)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    premium_subscriptions = models.IntegerField(default=0)
    featured_listings = models.IntegerField(default=0)
    transaction_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('date',)

    def __str__(self):
        return f"Revenue Analytics for {self.date}"
