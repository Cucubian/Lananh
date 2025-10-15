from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Khách hàng'),
        ('owner', 'Chủ sân'),
        ('staff', 'Nhân viên'),
    ]
    
    full_name = models.CharField('Họ và tên', max_length=255)
    phone = models.CharField('Số điện thoại', max_length=15, blank=True)
    address = models.TextField('Địa chỉ', blank=True)
    role = models.CharField('Vai trò', max_length=20, choices=ROLE_CHOICES, default='customer')
    avatar = models.ImageField('Ảnh đại diện', upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Ngày cập nhật', auto_now=True)
    
    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
    
    @property
    def is_customer(self):
        return self.role == 'customer'
    
    @property
    def is_owner(self):
        return self.role == 'owner'
    
    @property
    def is_staff_member(self):
        return self.role == 'staff'
