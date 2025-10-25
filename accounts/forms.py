from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import User

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Your phone number'})
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Your address'})
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        initial='buyer',
        label="Account Type (Required)",
        help_text="Select your role: Property Buyer or Real Estate Broker"
    )
    agree_terms = forms.BooleanField(
        required=True,
        label=mark_safe('I agree to the <a href="/legal/privacy-policy/" '
                        'target="_blank">Privacy Policy</a> and '
                        '<a href="/legal/terms-of-service/" target="_blank">'
                        'Terms of Service</a>.'),
        error_messages={
            'required': 'You must agree to the Privacy Policy and Terms '
                        'of Service to register.'
        }
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.agree_terms = self.cleaned_data['agree_terms']
        user.terms_accepted_date = timezone.now() if self.cleaned_data[
            'agree_terms'] else None
        user.phone_number = self.cleaned_data.get('phone_number') or ''
        user.address = self.cleaned_data.get('address') or ''
        user.user_type = self.cleaned_data.get('user_type', 'buyer')
        if commit:
            user.save()
        return user

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2')  # Removed email field


class CustomAuthenticationForm(AuthenticationForm):
    pass


# Import SignupForm inside the function to avoid circular import
def create_custom_signup_form():
    from allauth.account.forms import SignupForm

    class CustomAllauthSignupForm(SignupForm):
        phone_number = forms.CharField(
            max_length=20,
            required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Phone Number'})
        )
        address = forms.CharField(
            max_length=255,
            required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Address'})
        )
        user_type = forms.ChoiceField(
            choices=User.USER_TYPE_CHOICES,
            initial='buyer',
            widget=forms.Select()
        )
        agree_terms = forms.BooleanField(
            required=True,
            label=mark_safe('I agree to the <a href="/legal/privacy-policy/" '
                            'target="_blank">Privacy Policy</a> and '
                            '<a href="/legal/terms-of-service/" '
                            'target="_blank">Terms of Service</a>.'),
            error_messages={
                'required': 'You must agree to the Privacy Policy and Terms '
                            'of Service to register.'
            }
        )

        def save(self, request):
            # Save the user using allauth's save method
            user = super().save(request)

            # Update additional fields
            user.agree_terms = self.cleaned_data['agree_terms']
            user.terms_accepted_date = timezone.now() if self.cleaned_data[
                'agree_terms'] else None
            user.phone_number = self.cleaned_data.get('phone_number', '')
            user.address = self.cleaned_data.get('address', '')
            user.user_type = self.cleaned_data.get('user_type', 'buyer')

            user.save()
            return user

    return CustomAllauthSignupForm


CustomAllauthSignupForm = create_custom_signup_form()
