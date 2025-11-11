from django.contrib import admin
from .models import Payment, BankAccount

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['bank_name', 'account_name', 'account_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'bank_name']
    search_fields = ['bank_name', 'account_name', 'account_number']
    list_editable = ['is_active']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['reference', 'order', 'amount', 'payment_method', 'status', 'paid_at', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['reference', 'transaction_id', 'order__order_number']
    readonly_fields = ['reference', 'created_at', 'updated_at', 'paid_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'reference', 'amount', 'payment_method', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'gateway_response', 'paid_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

