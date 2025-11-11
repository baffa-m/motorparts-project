from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone_no = models.CharField(max_length=15)  # Increased for international numbers
    email = models.EmailField(unique=True, max_length=254)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return self.email

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"
