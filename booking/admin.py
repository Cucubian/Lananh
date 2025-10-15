from django.contrib import admin
from .models import Court, TimeSlot, Booking

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_hour', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['time', 'get_time_display']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['customer', 'court', 'date', 'total_hours', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'date', 'created_at']
    search_fields = ['customer__full_name', 'customer__username', 'court__name']
    list_editable = ['status']
    date_hierarchy = 'date'
    filter_horizontal = ['time_slots']
