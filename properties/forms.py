from django import forms
from .models import Property, PropertyType, Amenity

class PropertySearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=False, label='Keywords')
    property_type = forms.ModelChoiceField(queryset=PropertyType.objects.all(), required=False, label='Property Type')
    min_price = forms.DecimalField(max_digits=15, decimal_places=2, required=False, label='Min Price')
    max_price = forms.DecimalField(max_digits=15, decimal_places=2, required=False, label='Max Price')
    min_sq_ft = forms.IntegerField(required=False, label='Min Square Footage')
    max_sq_ft = forms.IntegerField(required=False, label='Max Square Footage')
    amenities = forms.ModelMultipleChoiceField(queryset=Amenity.objects.all(), required=False, widget=forms.CheckboxSelectMultiple, label='Amenities')

    # Add more fields for other filters like location, year built, zoning, etc.
    city = forms.CharField(max_length=100, required=False, label='City')
    state = forms.CharField(max_length=100, required=False, label='State')
    zip_code = forms.CharField(max_length=20, required=False, label='Zip Code')
    lease_or_buy = forms.ChoiceField(choices=[('', 'Any')] + list(Property.PROPERTY_STATUS_CHOICES), required=False, label='Lease/Buy')
    cap_rate = forms.DecimalField(max_digits=5, decimal_places=2, required=False, label='Cap Rate')
    year_built = forms.IntegerField(required=False, label='Year Built')
    zoning = forms.CharField(max_length=100, required=False, label='Zoning')

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'address', 'city', 'state', 
            'zip_code', 'country', 'price', 'square_footage', 'lot_size', 
            'year_built', 'zoning', 'status', 'amenities', 'cap_rate', 'noi', 
            'rent_roll', 'expense_summaries', 'broker_name', 'broker_email', 
            'broker_phone', 'virtual_tour_url', 'floor_plan_image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'rent_roll': forms.Textarea(attrs={'rows': 4}),
            'expense_summaries': forms.Textarea(attrs={'rows': 4}),
        }