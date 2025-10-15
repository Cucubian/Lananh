from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Court(models.Model):
    name = models.CharField('Tên sân', max_length=100)
    description = models.TextField('Mô tả', blank=True)
    price_per_hour = models.DecimalField('Giá/giờ', max_digits=10, decimal_places=0, validators=[MinValueValidator(0)])
    image = models.ImageField('Hình ảnh', upload_to='courts/', blank=True, null=True)
    is_active = models.BooleanField('Đang hoạt động', default=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Ngày cập nhật', auto_now=True)
    
    class Meta:
        verbose_name = 'Sân'
        verbose_name_plural = 'Sân'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    TIME_CHOICES = [
        ('06:00', '06:00 - 07:00'),
        ('07:00', '07:00 - 08:00'),
        ('08:00', '08:00 - 09:00'),
        ('09:00', '09:00 - 10:00'),
        ('10:00', '10:00 - 11:00'),
        ('11:00', '11:00 - 12:00'),
        ('12:00', '12:00 - 13:00'),
        ('13:00', '13:00 - 14:00'),
        ('14:00', '14:00 - 15:00'),
        ('15:00', '15:00 - 16:00'),
        ('16:00', '16:00 - 17:00'),
        ('17:00', '17:00 - 18:00'),
        ('18:00', '18:00 - 19:00'),
        ('19:00', '19:00 - 20:00'),
        ('20:00', '20:00 - 21:00'),
        ('21:00', '21:00 - 22:00'),
    ]
    
    time = models.CharField('Khung giờ', max_length=5, choices=TIME_CHOICES, unique=True)
    
    class Meta:
        verbose_name = 'Khung giờ'
        verbose_name_plural = 'Khung giờ'
        ordering = ['time']
    
    def __str__(self):
        return self.get_time_display()

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
        ('completed', 'Hoàn thành'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', verbose_name='Khách hàng')
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='bookings', verbose_name='Sân')
    date = models.DateField('Ngày đặt')
    time_slots = models.ManyToManyField(TimeSlot, verbose_name='Khung giờ')
    total_hours = models.PositiveIntegerField('Tổng số giờ', default=1)
    total_price = models.DecimalField('Tổng tiền', max_digits=10, decimal_places=0, default=0)
    status = models.CharField('Trạng thái', max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_proof = models.ImageField('Minh chứng thanh toán', upload_to='payment_proofs/', blank=True, null=True)
    notes = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Ngày cập nhật', auto_now=True)
    
    class Meta:
        verbose_name = 'Đơn đặt sân'
        verbose_name_plural = 'Đơn đặt sân'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.court.name} - {self.date}"
    
    def save(self, *args, **kwargs):
        if self.pk:  # If this is an update
            self.total_price = self.court.price_per_hour * self.total_hours
        super().save(*args, **kwargs)
