from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from accounts.models import User
from booking.models import Booking, Court
from services.models import ServiceOrder, Service

def is_staff_or_owner(user):
    return user.is_authenticated and (user.is_owner or user.is_staff_member or user.is_superuser)

@login_required
@user_passes_test(is_staff_or_owner)
def dashboard(request):
    # Statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    total_revenue = Booking.objects.filter(status__in=['confirmed', 'completed']).aggregate(
        total=Sum('total_price'))['total'] or 0
    
    # Service statistics
    total_service_orders = ServiceOrder.objects.count()
    service_revenue = ServiceOrder.objects.filter(status='completed').aggregate(
        total=Sum('total_price'))['total'] or 0
    
    # Recent bookings
    recent_bookings = Booking.objects.all()[:10]
    
    # Revenue by date (last 7 days)
    seven_days_ago = datetime.now().date() - timedelta(days=7)
    daily_revenue = Booking.objects.filter(
        created_at__date__gte=seven_days_ago,
        status__in=['confirmed', 'completed']
    ).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        revenue=Sum('total_price')
    ).order_by('day')
    
    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue,
        'total_service_orders': total_service_orders,
        'service_revenue': service_revenue,
        'recent_bookings': recent_bookings,
        'daily_revenue': daily_revenue,
    }
    
    return render(request, 'management/dashboard.html', context)

@login_required
@user_passes_test(is_staff_or_owner)
def booking_management(request):
    bookings = Booking.objects.all()
    
    # Filters
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    date = request.GET.get('date')
    if date:
        bookings = bookings.filter(date=date)
    
    return render(request, 'management/booking_management.html', {'bookings': bookings})

@login_required
@user_passes_test(is_staff_or_owner)
def booking_update_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
            messages.success(request, f'Đã cập nhật trạng thái đơn đặt sân.')
            return redirect('management:booking_management')
    
    return render(request, 'management/booking_update_status.html', {'booking': booking})

@login_required
@user_passes_test(is_staff_or_owner)
def user_management(request):
    users = User.objects.all()
    
    # Filters
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(full_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    return render(request, 'management/user_management.html', {'users': users})

@login_required
@user_passes_test(is_staff_or_owner)
def revenue_report(request):
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    bookings = Booking.objects.filter(status__in=['confirmed', 'completed'])
    service_orders = ServiceOrder.objects.filter(status='completed')
    
    if start_date:
        bookings = bookings.filter(created_at__date__gte=start_date)
        service_orders = service_orders.filter(created_at__date__gte=start_date)
    
    if end_date:
        bookings = bookings.filter(created_at__date__lte=end_date)
        service_orders = service_orders.filter(created_at__date__lte=end_date)
    
    # Calculate totals
    booking_revenue = bookings.aggregate(total=Sum('total_price'))['total'] or 0
    service_revenue = service_orders.aggregate(total=Sum('total_price'))['total'] or 0
    total_revenue = booking_revenue + service_revenue
    
    # Revenue by court
    court_revenue = bookings.values('court__name').annotate(
        total=Sum('total_price'),
        count=Count('id')
    ).order_by('-total')
    
    # Revenue by service category
    service_category_revenue = ServiceOrder.objects.filter(
        status='completed'
    ).values('items__service__category').annotate(
        total=Sum('items__subtotal')
    )
    
    context = {
        'booking_revenue': booking_revenue,
        'service_revenue': service_revenue,
        'total_revenue': total_revenue,
        'court_revenue': court_revenue,
        'service_category_revenue': service_category_revenue,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'management/revenue_report.html', context)

@login_required
@user_passes_test(is_staff_or_owner)
def service_management(request):
    services = Service.objects.all()
    
    category = request.GET.get('category')
    if category:
        services = services.filter(category=category)
    
    return render(request, 'management/service_management.html', {'services': services})
