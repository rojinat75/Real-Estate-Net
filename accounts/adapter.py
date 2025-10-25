from allauth.account.adapter import DefaultAccountAdapter
from django.utils.safestring import mark_safe

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_signup_form_class(self, request):
        return self.create_custom_signup_form()

    def create_custom_signup_form(self):
        from allauth.account.forms import SignupForm
        from django import forms
        from django.utils import timezone
        from .models import User

        class CustomAllauthSignupForm(SignupForm):
            phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
            address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': 'Address'}))
            user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, initial='buyer', widget=forms.Select())
            agree_terms = forms.BooleanField(
                required=True,
                label=mark_safe('I agree to the <a href="/legal/privacy-policy/" target="_blank">Privacy Policy</a> and <a href="/legal/terms-of-service/" target="_blank">Terms of Service</a>.'),
                error_messages={
                    'required': 'You must agree to the Privacy Policy and Terms of Service to register.'
                }
            )

            def save(self, request):
                # Save the user using allauth's save method
                user = super().save(request)

                # Update additional fields
                user.agree_terms = self.cleaned_data['agree_terms']
                user.terms_accepted_date = timezone.now() if self.cleaned_data['agree_terms'] else None
                user.phone_number = self.cleaned_data.get('phone_number', '')
                user.address = self.cleaned_data.get('address', '')
                user.user_type = self.cleaned_data.get('user_type', 'buyer')

                user.save()
                return user

        return CustomAllauthSignupForm
