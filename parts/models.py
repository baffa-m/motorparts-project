from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name
        
class Manufacturer(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="manufacturers")
    
    def __str__(self):
            return self.name

class Part(models.Model):
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('tourist', 'Tourist'),
        ('used', 'Used')
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    part_number = models.CharField(max_length=20)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    stock_quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to="parts")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("part_detail", kwargs={"slug": self.slug})
    
    