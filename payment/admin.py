from django.contrib import admin
from .models import Payment, PaymentLog

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'booking', 'amount', 'payment_method', 'status', 'created_at', 'paid_at']
    list_filter = ['status', 'payment_method', 'created_at', 'paid_at']
    search_fields = ['id', 'user__username', 'user__full_name', 'vnpay_transaction_no', 'vnpay_txn_ref']
    readonly_fields = ['id', 'created_at', 'updated_at', 'paid_at', 'vnpay_transaction_no', 'vnpay_txn_ref', 'vnpay_response_code', 'vnpay_secure_hash']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('id', 'user', 'booking', 'amount', 'currency', 'payment_method', 'status')
        }),
        ('Thông tin VNPay', {
            'fields': ('vnpay_txn_ref', 'vnpay_order_info', 'vnpay_transaction_no', 'vnpay_response_code', 'vnpay_bank_code', 'vnpay_card_type', 'vnpay_pay_date', 'vnpay_secure_hash'),
            'classes': ('collapse',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'expired_at')
        }),
        ('Thông tin bổ sung', {
            'fields': ('description', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'booking', 'booking__court')

@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['payment', 'action', 'message', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['payment__id', 'message']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment', 'payment__user')
