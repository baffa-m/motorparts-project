from django.db import models
from orders.models import Order

class BankAccount(models.Model):
    """Store company bank accounts for receiving payments"""
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=20)
    sort_code = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_active', 'bank_name']
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD = [
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    gateway_response = models.JSONField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.reference} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']

