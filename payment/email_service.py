from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_payment_success_email(payment, booking):
        """
        Gửi email thông báo thanh toán thành công
        """
        try:
            # Chuẩn bị dữ liệu cho template
            context = {
                'user': payment.user,
                'payment': payment,
                'booking': booking,
                'court': booking.court if booking else None,
                'site_name': 'CourtMaster',
                'site_url': 'http://localhost:8000'  # Có thể lấy từ settings
            }
            
            # Render HTML template
            html_message = render_to_string('payment/emails/payment_success.html', context)
            
            # Render text version
            text_message = render_to_string('payment/emails/payment_success.txt', context)
            
            # Gửi email
            send_mail(
                subject=f'[CourtMaster] Thanh toán thành công - Đơn đặt sân #{booking.id if booking else "N/A"}',
                message=text_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[payment.user.email],
                fail_silently=False,
            )
            
            logger.info(f"Payment success email sent to {payment.user.email} for payment {payment.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send payment success email: {str(e)}")
            return False
    
    @staticmethod
    def send_payment_failed_email(payment, booking):
        """
        Gửi email thông báo thanh toán thất bại
        """
        try:
            context = {
                'user': payment.user,
                'payment': payment,
                'booking': booking,
                'court': booking.court if booking else None,
                'site_name': 'CourtMaster',
                'site_url': 'http://localhost:8000'
            }
            
            html_message = render_to_string('payment/emails/payment_failed.html', context)
            text_message = render_to_string('payment/emails/payment_failed.txt', context)
            
            send_mail(
                subject=f'[CourtMaster] Thanh toán thất bại - Đơn đặt sân #{booking.id if booking else "N/A"}',
                message=text_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[payment.user.email],
                fail_silently=False,
            )
            
            logger.info(f"Payment failed email sent to {payment.user.email} for payment {payment.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send payment failed email: {str(e)}")
            return False
