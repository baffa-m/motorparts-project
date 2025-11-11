from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta: 
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "password1", "password2"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CustomUserAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )