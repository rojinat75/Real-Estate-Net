from django.db import models
from django.conf import settings

class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=(
        ('city', 'City'),
        ('district', 'District'),
        ('region', 'Region'),
        ('neighborhood', 'Neighborhood'),
    ))
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Nepal')
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('name', 'type', 'state')

    def __str__(self):
        return f"{self.name} ({self.type})"

class PropertyType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SavedSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100)
    filters = models.TextField()  # Store URL encoded query string
    alert_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.user.username}"

class Property(models.Model):
    PROPERTY_STATUS_CHOICES = (
        ('for_sale', 'For Sale'),
        ('for_lease', 'For Lease'),
        ('sold', 'Sold'),
        ('leased', 'Leased'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True, related_name='properties')
    address = models.CharField(max_length=255)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Nepal')
    price = models.DecimalField(max_digits=15, decimal_places=2)
    square_footage = models.IntegerField(blank=True, null=True)
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    year_built = models.IntegerField(blank=True, null=True)
    zoning = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PROPERTY_STATUS_CHOICES, default='for_sale')
    amenities = models.ManyToManyField(Amenity, blank=True)
    
    # Financial Data
    cap_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    noi = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True) # Net Operating Income
    rent_roll = models.TextField(blank=True, null=True) # Can be a JSON field or a separate model if complex
    expense_summaries = models.TextField(blank=True, null=True) # Can be a JSON field or a separate model if complex

    # Contact Information
    broker_name = models.CharField(max_length=255, blank=True, null=True)
    broker_email = models.EmailField(blank=True, null=True)
    broker_phone = models.CharField(max_length=20, blank=True, null=True)

    # Multimedia
    virtual_tour_url = models.URLField(blank=True, null=True)
    floor_plan_image = models.ImageField(upload_to='floor_plans/', blank=True, null=True)

    # Premium status
    is_premium = models.BooleanField(default=False)

    # Verification status
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Image(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.property.title}"
