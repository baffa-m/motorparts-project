from django.db import models
from orders.models import Order

class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days_min = models.IntegerField()
    estimated_days_max = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_duration_display(self):
        if self.estimated_days_min == self.estimated_days_max:
            return f"{self.estimated_days_min} business days"
        return f"{self.estimated_days_min}-{self.estimated_days_max} business days"

class Shipment(models.Model):
    SHIPMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed Delivery'),
        ('returned', 'Returned'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    tracking_number = models.CharField(max_length=100, unique=True)
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=SHIPMENT_STATUS, default='pending')
    carrier = models.CharField(max_length=100, blank=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Shipment {self.tracking_number} for {self.order.order_number}"

class ShipmentTracking(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.status} - {self.location}"
