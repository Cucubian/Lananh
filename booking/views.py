from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Court, Booking, TimeSlot
from .forms import BookingForm, PaymentProofForm
from datetime import date

def court_list(request):
    courts = Court.objects.filter(is_active=True)
    return render(request, 'booking/court_list.html', {'courts': courts})

@login_required
def booking_create(request, court_id=None):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.total_hours = form.cleaned_data['time_slots'].count()
            booking.total_price = booking.court.price_per_hour * booking.total_hours
            booking.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Đặt sân thành công! Vui lòng thanh toán và upload minh chứng.')
            return redirect('booking:booking_detail', pk=booking.pk)
    else:
        initial = {}
        if court_id:
            initial['court'] = court_id
        form = BookingForm(initial=initial)
    
    return render(request, 'booking/booking_create.html', {'form': form})

@login_required
def booking_list(request):
    if request.user.is_customer:
        bookings = Booking.objects.filter(customer=request.user)
    else:
        bookings = Booking.objects.all()
    
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    return render(request, 'booking/booking_list.html', {'bookings': bookings})

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check permissions
    if request.user.is_customer and booking.customer != request.user:
        messages.error(request, 'Bạn không có quyền xem đơn đặt này.')
        return redirect('booking:booking_list')
    
    return render(request, 'booking/booking_detail.html', {'booking': booking})

@login_required
def booking_upload_payment(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    
    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Upload minh chứng thanh toán thành công!')
            return redirect('booking:booking_detail', pk=booking.pk)
    else:
        form = PaymentProofForm(instance=booking)
    
    return render(request, 'booking/booking_upload_payment.html', {'form': form, 'booking': booking})

@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check permissions
    if request.user.is_customer and booking.customer != request.user:
        messages.error(request, 'Bạn không có quyền hủy đơn đặt này.')
        return redirect('booking:booking_list')
    
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, 'Không thể hủy đơn đặt này.')
        return redirect('booking:booking_detail', pk=pk)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Đã hủy đơn đặt sân.')
        return redirect('booking:booking_list')
    
    return render(request, 'booking/booking_cancel.html', {'booking': booking})
