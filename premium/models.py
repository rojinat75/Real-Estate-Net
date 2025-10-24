from django.db import models
from properties.models import Property
from django.conf import settings
from django.utils import timezone


class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    code = models.CharField(max_length=20, unique=True, help_text="Unique promo code")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=8, decimal_places=2, help_text="Discount value (% or fixed amount)")
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=None, null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else 'NPR'}"

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.max_uses is None or self.times_used < self.max_uses)
        )

    def apply_discount(self, amount):
        if self.discount_type == 'percentage':
            return amount * (1 - self.discount_value / 100)
        else:
            return max(0, amount - self.discount_value)

    def use_code(self):
        if self.is_valid():
            self.times_used += 1
            self.save()
            return True
        return False

    class Meta:
        ordering = ['-created_at']

class EmailNotification(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('premium_activated', 'Premium Activated'),
        ('premium_expiring', 'Premium Expiring Soon'),
        ('premium_expired', 'Premium Expired'),
        ('payment_received', 'Payment Received'),
        ('payment_failed', 'Payment Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    recipient_email = models.EmailField()
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']

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
