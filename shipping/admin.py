from django.contrib import admin
from .models import ShippingMethod, Shipment, ShipmentTracking

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_cost', 'estimated_days_min', 'estimated_days_max', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'order', 'status', 'shipping_method', 'estimated_delivery_date', 'created_at']
    list_filter = ['status', 'shipping_method', 'created_at']
    search_fields = ['tracking_number', 'order__order_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'status', 'location', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['shipment__tracking_number', 'location']
    readonly_fields = ['timestamp']
