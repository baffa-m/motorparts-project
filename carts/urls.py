from django.urls import path
from . import views

app_name = 'carts'

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart_detail'),
    path('', views.CartDetailView.as_view(), name='detail'),
    path('add/<int:part_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_item'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_item'),
    path('clear/', views.clear_cart, name='clear'),
    path('count/', views.cart_count, name='count'),
]
