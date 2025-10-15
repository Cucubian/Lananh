from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bookings/', views.booking_management, name='booking_management'),
    path('bookings/<int:pk>/update-status/', views.booking_update_status, name='booking_update_status'),
    path('users/', views.user_management, name='user_management'),
    path('revenue/', views.revenue_report, name='revenue_report'),
    path('services/', views.service_management, name='service_management'),
]
