from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'full_name', 'phone', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('full_name', 'phone', 'address', 'role', 'avatar')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {'fields': ('full_name', 'phone', 'address', 'role', 'avatar')}),
    )
    search_fields = ['username', 'email', 'full_name', 'phone']

admin.site.register(User, CustomUserAdmin)
