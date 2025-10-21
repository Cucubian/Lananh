from django.shortcuts import render
from django.db.models import Count, Q
from booking.models import Court, Booking

def home_view(request):
    """Home view với dữ liệu động"""
    # Lấy 3 sân được đặt nhiều nhất (confirmed bookings)
    popular_courts = Court.objects.filter(
        is_active=True,
        bookings__status='confirmed'
    ).annotate(
        booking_count=Count('bookings', filter=Q(bookings__status='confirmed'))
    ).order_by('-booking_count')[:3]
    
    # Nếu không có sân nào được đặt, lấy 3 sân đầu tiên
    if not popular_courts:
        popular_courts = Court.objects.filter(is_active=True)[:3]
    
    context = {
        'popular_courts': popular_courts,
    }
    
    return render(request, 'home.html', context)
