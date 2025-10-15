from django.contrib import admin
from .models import Service, ServiceOrder, ServiceOrderItem

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_available', 'created_at']
    list_filter = ['category', 'is_available', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_available', 'stock']

class ServiceOrderItemInline(admin.TabularInline):
    model = ServiceOrderItem
    extra = 0
    readonly_fields = ['price', 'subtotal']

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'customer', 'booking', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__full_name', 'customer__username']
    list_editable = ['status']
    inlines = [ServiceOrderItemInline]
    readonly_fields = ['total_price']
