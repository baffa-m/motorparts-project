from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, CustomUserAuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile

# Register View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('parts:home')
    else:
        form = CustomUserCreationForm()
        
    return render(request, "auth/register.html", {"form": form})

# Login View
class Login(LoginView):
    template_name = "auth/login.html"
    authentication_form = CustomUserAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, 'Login successful!')
        return "/"

# Logout View
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect("accounts:login")

# Profile View
class CurrentUser(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'accounts/profile.html'
    context_object_name = "user"
    
    def get_object(self, queryset=None):
        return self.request.user

@login_required
def update_user_details(request):
    user = request.user

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_no = request.POST.get('phone_no', '').strip()

        User = get_user_model()

        # Check if email belongs to another user
        if email and User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, 'This email is already in use by another account.')
            return redirect('accounts:profile')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_no = phone_no
        user.save()

        messages.success(request, 'User details updated successfully!')
        return redirect('accounts:profile')


@login_required
def update_address_details(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        profile.address = request.POST.get('address', '').strip()
        profile.city = request.POST.get('city', '').strip()
        profile.state = request.POST.get('state', '').strip()
        profile.postal_code = request.POST.get('postal_code', '').strip()
        profile.save()

        messages.success(request, 'Address updated successfully!')
        return redirect('accounts:profile')


# Password Change View - NEW
@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Verify current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('accounts:profile')
        
        # Validate new password
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('accounts:profile')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('accounts:profile')
        
        # Change password
        request.user.set_password(new_password)
        request.user.save()
        
        # Re-login user
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('accounts:profile')
    
    return redirect('accounts:profile')

