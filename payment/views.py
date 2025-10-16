from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from booking.models import Booking
from .models import Payment, PaymentLog
from .vnpay_service import VNPayService
from .email_service import EmailService
import logging

logger = logging.getLogger(__name__)

# ==================== Payment Method Selection ====================
@login_required
def payment_method_selection(request, booking_id):
    """Chọn phương thức thanh toán"""
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'vnpay':
            return redirect('payment:create_vnpay_payment', booking_id=booking_id)
        elif payment_method == 'qr_code':
            return redirect('booking:booking_upload_payment', pk=booking_id)
        else:
            messages.error(request, "Phương thức thanh toán không hợp lệ.")
            return redirect('payment:payment_method_selection', booking_id=booking_id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'payment/payment_method.html', context)


# ==================== VNPay Payment ====================
@login_required
def create_vnpay_payment(request, booking_id):
    """Tạo thanh toán VNPay"""
    try:
        booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
        
        # Kiểm tra booking đã thanh toán chưa
        if booking.has_paid_payment():
            messages.warning(request, "Booking này đã được thanh toán.")
            return redirect('booking:booking_detail', pk=booking_id)
        
        # Tạo payment
        with transaction.atomic():
            payment = Payment.objects.create(
                user=request.user,
                booking=booking,
                amount=booking.total_price,
                payment_method='vnpay',
                status='pending',
                description=f'Thanh toán đặt sân {booking.court.name} - {booking.date}'
            )
            
            # Tạo log
            PaymentLog.objects.create(
                payment=payment,
                action='created',
                message=f'Tạo thanh toán VNPay cho booking {booking.id}',
                data={'booking_id': booking.id, 'amount': str(payment.amount)}
            )
        
        messages.success(request, "Đã tạo thanh toán thành công.")
        return redirect('payment:payment_detail', payment_id=payment.id)
        
    except Exception as e:
        logger.error(f"Error creating VNPay payment: {str(e)}")
        messages.error(request, f"Lỗi tạo thanh toán: {str(e)}")
        return redirect('booking:booking_detail', pk=booking_id)


@login_required
def payment_detail(request, payment_id):
    """Chi tiết thanh toán"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    logs = payment.logs.all()[:10]
    
    context = {
        'payment': payment,
        'logs': logs,
    }
    return render(request, 'payment/payment_detail.html', context)


@login_required
def vnpay_payment(request, payment_id):
    """Chuyển hướng đến VNPay"""
    try:
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        # Kiểm tra payment có thể thanh toán không
        if not payment.can_be_paid:
            messages.error(request, "Payment này không thể thanh toán.")
            return redirect('payment:payment_detail', payment_id=payment_id)
        
        # Tạo VNPay URL
        vnpay_service = VNPayService()
        payment_url = vnpay_service.create_payment_url(payment, request)
        
        # Cập nhật status
        payment.status = 'processing'
        payment.save()
        
        # Tạo log
        PaymentLog.objects.create(
            payment=payment,
            action='redirect_to_vnpay',
            message='Chuyển hướng đến VNPay',
            data={'url': payment_url}
        )
        
        logger.info(f"Redirecting to VNPay for payment {payment_id}")
        return redirect(payment_url)
        
    except Exception as e:
        logger.error(f"Error redirecting to VNPay: {str(e)}")
        messages.error(request, f"Lỗi chuyển hướng đến VNPay: {str(e)}")
        return redirect('payment:payment_detail', payment_id=payment_id)


@login_required
def vnpay_return(request):
    """Xử lý kết quả trả về từ VNPay"""
    try:
        # Lấy params từ VNPay
        vnpay_params = request.GET.dict()
        
        # Lấy txn_ref
        txn_ref = vnpay_params.get('vnp_TxnRef')
        if not txn_ref:
            messages.error(request, "Không tìm thấy mã giao dịch.")
            return redirect('booking:booking_list')
        
        # Tìm payment
        payment = Payment.objects.filter(vnpay_txn_ref=txn_ref).first()
        if not payment:
            messages.error(request, "Không tìm thấy thanh toán.")
            return redirect('booking:booking_list')
        
        # Verify signature
        vnpay_service = VNPayService()
        is_valid, message = vnpay_service.verify_payment_response(vnpay_params)
        
        if is_valid:
            # Thanh toán thành công
            with transaction.atomic():
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.vnpay_response_code = vnpay_params.get('vnp_ResponseCode')
                payment.vnpay_transaction_no = vnpay_params.get('vnp_TransactionNo')
                payment.vnpay_bank_code = vnpay_params.get('vnp_BankCode')
                payment.vnpay_card_type = vnpay_params.get('vnp_CardType')
                payment.vnpay_pay_date = vnpay_params.get('vnp_PayDate')
                payment.save()
                
                # Cập nhật booking
                if payment.booking:
                    payment.booking.status = 'confirmed'
                    payment.booking.save()
                
                # Tạo log
                PaymentLog.objects.create(
                    payment=payment,
                    action='payment_success',
                    message='Thanh toán VNPay thành công',
                    data=vnpay_params
                )
            
            # Gửi email thông báo thanh toán thành công
            try:
                EmailService.send_payment_success_email(payment, payment.booking)
                logger.info(f"Payment success email sent for payment {payment.id}")
            except Exception as e:
                logger.error(f"Failed to send payment success email: {str(e)}")
            
            messages.success(request, "Thanh toán thành công!")
            return redirect('payment:payment_success', payment_id=payment.id)
        else:
            # Thanh toán thất bại
            payment.status = 'failed'
            payment.vnpay_response_code = vnpay_params.get('vnp_ResponseCode')
            payment.description += f"\nLỗi: {message}"
            payment.save()
            
            # Tạo log
            PaymentLog.objects.create(
                payment=payment,
                action='payment_failed',
                message=f'Thanh toán VNPay thất bại: {message}',
                data=vnpay_params
            )
            
            messages.error(request, f"Thanh toán thất bại: {message}")
            return redirect('payment:payment_failed', payment_id=payment.id)
            
    except Exception as e:
        logger.error(f"Error processing VNPay return: {str(e)}")
        messages.error(request, f"Lỗi xử lý kết quả thanh toán: {str(e)}")
        return redirect('booking:booking_list')


@csrf_exempt
@require_http_methods(["GET", "POST"])
def vnpay_ipn(request):
    """Xử lý IPN từ VNPay"""
    try:
        # Lấy params từ VNPay
        vnpay_params = request.GET.dict()
        
        # Lấy txn_ref
        txn_ref = vnpay_params.get('vnp_TxnRef')
        if not txn_ref:
            return JsonResponse({'RspCode': '99', 'Message': 'Invalid txn_ref'})
        
        # Tìm payment
        payment = Payment.objects.filter(vnpay_txn_ref=txn_ref).first()
        if not payment:
            return JsonResponse({'RspCode': '01', 'Message': 'Order not found'})
        
        # Verify signature
        vnpay_service = VNPayService()
        is_valid, message = vnpay_service.verify_payment_response(vnpay_params)
        
        if not is_valid:
            return JsonResponse({'RspCode': '97', 'Message': 'Invalid signature'})
        
        # Kiểm tra amount
        vnp_amount = int(vnpay_params.get('vnp_Amount', 0))
        if vnp_amount != int(payment.amount * 100):
            return JsonResponse({'RspCode': '04', 'Message': 'Invalid amount'})
        
        # Kiểm tra trạng thái payment
        if payment.status == 'completed':
            return JsonResponse({'RspCode': '02', 'Message': 'Order already confirmed'})
        
        # Cập nhật payment
        response_code = vnpay_params.get('vnp_ResponseCode')
        if response_code == '00':
            with transaction.atomic():
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.vnpay_response_code = response_code
                payment.vnpay_transaction_no = vnpay_params.get('vnp_TransactionNo')
                payment.vnpay_bank_code = vnpay_params.get('vnp_BankCode')
                payment.vnpay_card_type = vnpay_params.get('vnp_CardType')
                payment.vnpay_pay_date = vnpay_params.get('vnp_PayDate')
                payment.save()
                
                # Cập nhật booking
                if payment.booking:
                    payment.booking.status = 'confirmed'
                    payment.booking.save()
                
                # Tạo log
                PaymentLog.objects.create(
                    payment=payment,
                    action='ipn_received',
                    message='Nhận IPN từ VNPay - Thanh toán thành công',
                    data=vnpay_params
                )
            
            # Gửi email thông báo thanh toán thành công (từ IPN)
            try:
                EmailService.send_payment_success_email(payment, payment.booking)
                logger.info(f"Payment success email sent via IPN for payment {payment.id}")
            except Exception as e:
                logger.error(f"Failed to send payment success email via IPN: {str(e)}")
            
            return JsonResponse({'RspCode': '00', 'Message': 'Success'})
        else:
            payment.status = 'failed'
            payment.vnpay_response_code = response_code
            payment.save()
            
            # Tạo log
            PaymentLog.objects.create(
                payment=payment,
                action='ipn_received',
                message=f'Nhận IPN từ VNPay - Thanh toán thất bại: {response_code}',
                data=vnpay_params
            )
            
            return JsonResponse({'RspCode': '00', 'Message': 'Success'})
            
    except Exception as e:
        logger.error(f"Error processing VNPay IPN: {str(e)}")
        return JsonResponse({'RspCode': '99', 'Message': str(e)})


# ==================== Payment Result Pages ====================
@login_required
def payment_success(request, payment_id):
    """Trang thanh toán thành công"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payment/payment_success.html', context)


@login_required
def payment_failed(request, payment_id):
    """Trang thanh toán thất bại"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payment/payment_failed.html', context)


# ==================== Payment Management ====================
@login_required
def payment_list(request):
    """Danh sách thanh toán"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    return render(request, 'payment/payment_list.html', context)


@login_required
def cancel_payment(request, payment_id):
    """Hủy thanh toán"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status == 'pending':
        payment.mark_as_cancelled()
        
        # Tạo log
        PaymentLog.objects.create(
            payment=payment,
            action='cancelled',
            message='Người dùng hủy thanh toán',
            data={}
        )
        
        messages.success(request, "Đã hủy thanh toán.")
    else:
        messages.error(request, "Không thể hủy thanh toán này.")
    
    return redirect('payment:payment_detail', payment_id=payment_id)


@login_required
def retry_payment(request, payment_id):
    """Thử lại thanh toán"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status in ['failed', 'cancelled']:
        # Tạo payment mới
        if payment.booking:
            return redirect('payment:payment_method_selection', booking_id=payment.booking.id)
        else:
            messages.error(request, "Không tìm thấy booking để thử lại thanh toán.")
    else:
        messages.error(request, "Không thể thử lại thanh toán này.")
    
    return redirect('payment:payment_detail', payment_id=payment_id)


# ==================== API ====================
@login_required
def payment_status_api(request, payment_id):
    """API lấy trạng thái thanh toán"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    data = {
        'id': str(payment.id),
        'status': payment.status,
        'amount': float(payment.amount),
        'payment_method': payment.payment_method,
        'created_at': payment.created_at.isoformat(),
        'paid_at': payment.paid_at.isoformat() if payment.paid_at else None,
    }
    
    return JsonResponse(data)
