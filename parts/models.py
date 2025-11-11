from django.db import models
from django.urls import reverse
from djmoney.models.fields import MoneyField
from django.core.validators import MinValueValidator
from djmoney.models.validators import MinMoneyValidator
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="manufacturers", blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Part(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('refurbished', 'Refurbished'),
        ('used', 'Used')
    ]
    
    VEHICLE_TYPE_CHOICES = [
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('truck', 'Truck'),
        ('suv', 'SUV'),
        ('van', 'Van'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = MoneyField(
        max_digits=10, 
        decimal_places=2, 
        default_currency='NGN',
        validators=[MinMoneyValidator(0)]
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, null=True, blank=True, on_delete=models.SET_NULL)
    part_number = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to="parts")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("parts:detail", kwargs={"pk": self.pk})
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0