from django.db import models
from properties.models import Property
from django.conf import settings
from django.utils import timezone

class PremiumListing(models.Model):
    PLAN_CHOICES = (
        ('basic', 'Basic Premium'),
        ('featured', 'Featured Listing'),
        ('premium', 'Premium Plus'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('qr_payment', 'QR Code Payment'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash Payment'),
        ('cheque', 'Cheque'),
        ('mobile_banking', 'Mobile Banking'),
    )

    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='premium_listing')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=100, blank=True, null=True, help_text="Transaction reference number")
    payment_details = models.JSONField(blank=True, null=True, help_text="Additional payment information")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Premium: {self.property.title}"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"PREM_{timezone.now().strftime('%Y%m%d%H%M%S')}_{self.property.id}"
        super().save(*args, **kwargs)

    def days_remaining(self):
        if self.end_date > timezone.now():
            return (self.end_date - timezone.now()).days
        return 0

    def is_expired(self):
        return self.end_date <= timezone.now()

    def is_expiring_soon(self):
        return self.days_remaining() <= 7 and not self.is_expired()

    class Meta:
        ordering = ['-created_at']
