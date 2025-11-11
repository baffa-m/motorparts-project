from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    path('calculate/', views.calculate_shipping, name='calculate'),
    path('track/<int:order_id>/', views.track_shipment, name='track'),
    path('rates/', views.get_shipping_rates, name='rates'),
]
