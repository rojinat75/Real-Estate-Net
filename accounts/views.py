from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home') # Assuming a 'home' URL exists
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('home') # Assuming a 'home' URL exists
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home') # Assuming a 'home' URL exists

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address']

@login_required
def dashboard(request):
    user_form = UserProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'username' in request.POST:  # profile update
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('accounts:dashboard')
        elif 'old_password' in request.POST:  # password change
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect('accounts:dashboard')
            else:
                messages.error(request, "Error changing password.")
    else:
        user_form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'accounts/dashboard.html', {'form': user_form, 'password_form': password_form})

@login_required
def delete_account(request):
    """View for users to delete their own account"""
    if request.method == 'POST':
        # Double confirmation check
        confirmation = request.POST.get('confirm_deletion', '')
        username = request.POST.get('confirm_username', '')

        if confirmation == 'DELETE' and username == request.user.username:
            # Delete user's properties first
            properties_count = request.user.properties.all().count()
            request.user.properties.all().delete()  # This will cascade delete related images

            # Delete the user account
            user_to_delete = request.user
            username = user_to_delete.username
            user_to_delete.delete()

            # Log out the user (they're already deleted so this is just cleanup)
            messages.success(request, f"Account '{username}' has been successfully deleted along with {properties_count} properties.")

            # Redirect to home page since user is now anonymous
            return redirect('home')

        else:
            messages.error(request, "Account deletion confirmation failed. Please type 'DELETE' and your username exactly.")

    return render(request, 'accounts/delete_account.html', {})
