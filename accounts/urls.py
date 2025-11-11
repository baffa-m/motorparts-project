from django.urls import path
from . import views

app_name = "accounts" 

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.CurrentUser.as_view(), name='profile'),
    path('profile/update/', views.update_user_details, name='update_profile'),
    path('profile/update-address/', views.update_address_details, name='update_address'),
    path('profile/change-password/', views.change_password, name='change_password'),
]