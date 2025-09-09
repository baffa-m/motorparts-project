from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta: 
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "password1", "password2"]


class CustomUserAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
    password = forms.PasswordInput()