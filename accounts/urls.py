from django.urls import path
from . import views


app_name = "accounts" 

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.Login.as_view(), name='login'),
    path('', views.CurrentUser.as_view(), name='profile'),
]
