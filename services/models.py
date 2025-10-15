from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from booking.models import Booking

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('drink', 'Nước uống'),
        ('equipment', 'Thiết bị'),
        ('other', 'Khác'),
    ]
    
    name = models.CharField('Tên dịch vụ', max_length=200)
    category = models.CharField('Loại dịch vụ', max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField('Mô tả', blank=True)
    price = models.DecimalField('Giá', max_digits=10, decimal_places=0, validators=[MinValueValidator(0)])
    image = models.ImageField('Hình ảnh', upload_to='services/', blank=True, null=True)
    stock = models.PositiveIntegerField('Số lượng tồn kho', default=0)
    is_available = models.BooleanField('Còn hàng', default=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Ngày cập nhật', auto_now=True)
    
    class Meta:
        verbose_name = 'Dịch vụ'
        verbose_name_plural = 'Dịch vụ'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"

class ServiceOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_orders', verbose_name='Khách hàng')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_orders', verbose_name='Đơn đặt sân')
    status = models.CharField('Trạng thái', max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField('Tổng tiền', max_digits=10, decimal_places=0, default=0)
    notes = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Ngày cập nhật', auto_now=True)
    
    class Meta:
        verbose_name = 'Đơn hàng dịch vụ'
        verbose_name_plural = 'Đơn hàng dịch vụ'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Đơn #{self.pk} - {self.customer.full_name}"
    
    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save()
        return total

class ServiceOrderItem(models.Model):
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name='items', verbose_name='Đơn hàng')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Dịch vụ')
    quantity = models.PositiveIntegerField('Số lượng', default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField('Đơn giá', max_digits=10, decimal_places=0)
    subtotal = models.DecimalField('Thành tiền', max_digits=10, decimal_places=0)
    
    class Meta:
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'
    
    def __str__(self):
        return f"{self.service.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.price = self.service.price
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
        self.order.calculate_total()
