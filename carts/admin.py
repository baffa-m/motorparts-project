from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'get_total_items', 'get_total_price', 'created_at')
    list_filter = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Total Price'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'part', 'quantity', 'get_total_price', 'created_at')
    list_filter = ('created_at', 'updated_at')
