from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at', 'updated_at')
    search_fields = ('order_number', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'payment_method')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'shipping_amount', 'total_amount')
        }),
        ('Shipping Address', {
            'fields': ('shipping_first_name', 'shipping_last_name', 'shipping_address', 
                      'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'part', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order__created_at',)
