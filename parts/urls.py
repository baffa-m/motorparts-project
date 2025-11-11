from django.urls import path
from . import views

app_name = "parts" 

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.PartsListView.as_view(), name='index'),
    path('products/<int:pk>/', views.PartDetailView.as_view(), name='detail'),
    path('manufacturers/', views.ManufacturerListView.as_view(), name='manufacturers'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
]