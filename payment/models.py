from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Đã thanh toán'),
        ('failed', 'Thanh toán thất bại'),
        ('cancelled', 'Đã hủy'),
        ('refunded', 'Đã hoàn tiền'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('vnpay', 'VNPay'),
        ('qr_code', 'QR Code'),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    booking = models.ForeignKey('booking.Booking', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    # Payment Details
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Số tiền thanh toán (VND)")
    currency = models.CharField(max_length=3, default='VND')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='vnpay')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # VNPay Specific
    vnpay_txn_ref = models.CharField(max_length=50, blank=True, null=True, help_text="Mã giao dịch VNPay")
    vnpay_order_info = models.CharField(max_length=255, blank=True, null=True, help_text="Thông tin đơn hàng VNPay")
    vnpay_response_code = models.CharField(max_length=10, blank=True, null=True, help_text="Mã phản hồi VNPay")
    vnpay_transaction_no = models.CharField(max_length=50, blank=True, null=True, help_text="Mã giao dịch VNPay")
    vnpay_bank_code = models.CharField(max_length=20, blank=True, null=True, help_text="Mã ngân hàng VNPay")
    vnpay_card_type = models.CharField(max_length=20, blank=True, null=True, help_text="Loại thẻ VNPay")
    vnpay_pay_date = models.CharField(max_length=20, blank=True, null=True, help_text="Ngày thanh toán VNPay")
    vnpay_secure_hash = models.CharField(max_length=255, blank=True, null=True, help_text="Chữ ký VNPay")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian thanh toán thành công")
    expired_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian hết hạn thanh toán")
    
    # Additional Info
    description = models.TextField(blank=True, help_text="Mô tả giao dịch")
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="IP của người thanh toán")
    user_agent = models.TextField(blank=True, help_text="User agent của người thanh toán")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Thanh toán'
        verbose_name_plural = 'Thanh toán'
    
    def __str__(self):
        return f"Payment {self.id} - {self.amount} VND - {self.get_status_display()}"
    
    @property
    def is_paid(self):
        return self.status == 'completed'
    
    @property
    def is_expired(self):
        if self.expired_at:
            return timezone.now() > self.expired_at
        return False
    
    @property
    def can_be_paid(self):
        return self.status == 'pending' and not self.is_expired
    
    def mark_as_paid(self):
        """Đánh dấu thanh toán thành công"""
        self.status = 'completed'
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at'])
        
        # Cập nhật trạng thái booking nếu có
        if self.booking:
            self.booking.status = 'confirmed'
            self.booking.save(update_fields=['status'])
    
    def mark_as_failed(self, reason=None):
        """Đánh dấu thanh toán thất bại"""
        self.status = 'failed'
        if reason:
            self.description += f"\nLý do thất bại: {reason}"
        self.save(update_fields=['status', 'description'])
    
    def mark_as_cancelled(self):
        """Đánh dấu thanh toán bị hủy"""
        self.status = 'cancelled'
        self.save(update_fields=['status'])
        
        # Cập nhật trạng thái booking nếu có
        if self.booking:
            self.booking.status = 'cancelled'
            self.booking.save(update_fields=['status'])


class PaymentLog(models.Model):
    """Log các hoạt động thanh toán"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=50, help_text="Hành động: created, paid, failed, etc.")
    message = models.TextField(help_text="Thông điệp log")
    data = models.JSONField(default=dict, blank=True, help_text="Dữ liệu bổ sung")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log thanh toán'
        verbose_name_plural = 'Log thanh toán'
    
    def __str__(self):
        return f"{self.payment.id} - {self.action} - {self.created_at}"
