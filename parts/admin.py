from django.contrib import admin
from .models import Part, Category, Manufacturer
# Register your models here.


admin.site.register(Part)
admin.site.register(Manufacturer)
admin.site.register(Category)