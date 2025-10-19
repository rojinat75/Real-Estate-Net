from django import forms
from .models import PremiumListing

class PremiumListingForm(forms.ModelForm):
    class Meta:
        model = PremiumListing
        fields = ['property', 'plan_type', 'end_date', 'amount_paid', 'payment_id']
