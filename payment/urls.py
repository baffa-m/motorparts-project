from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('initiate/<int:order_id>/', views.initiate_payment, name='initiate'),
    path('bank-transfer/<int:order_id>/', views.bank_transfer_payment, name='bank_transfer'),
    path('confirm-transfer/<int:order_id>/', views.confirm_transfer, name='confirm_transfer'),
    path('callback/', views.payment_callback, name='callback'),
    path('verify/<str:reference>/', views.verify_payment, name='verify'),
    path('success/<int:order_id>/', views.payment_success, name='success'),
    path('failed/<int:order_id>/', views.payment_failed, name='failed'),
]
