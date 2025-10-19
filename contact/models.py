from django.db import models

class ContactInquiry(models.Model):
    INQUIRY_TYPE_CHOICES = (
        ('general', 'General Inquiry'),
        ('property', 'Property Inquiry'),
        ('support', 'Technical Support'),
        ('partnership', 'Partnership'),
        ('complaint', 'Complaint'),
    )

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPE_CHOICES, default='general')
    property = models.ForeignKey('properties.Property', on_delete=models.SET_NULL, null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inquiry: {self.name}"
