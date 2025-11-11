from django.db import models
from parts.models import Part
from accounts.models import User
# Create your models here.


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        unique_together = ('user', 'session_key')
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Anonymous Cart ({self.session_key})"
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        unique_together = ('cart', 'part')
    
    def get_total_price(self):
        return self.quantity * self.part.price.amount
    
    def __str__(self):
        return f"{self.quantity} x {self.part.name}"
