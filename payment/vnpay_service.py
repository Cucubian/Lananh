import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class VNPayService:
    """Service xử lý thanh toán VNPay"""
    
    def __init__(self):
        self.vnp_url = settings.VNPAY_URL
        self.vnp_tmn_code = settings.VNPAY_TMN_CODE
        self.vnp_secret_key = settings.VNPAY_SECRET_KEY
        self.vnp_return_url = settings.VNPAY_RETURN_URL
        self.vnp_version = '2.1.0'
        self.vnp_command = 'pay'
        self.vnp_mock = getattr(settings, 'VNPAY_MOCK', False)
    
    def create_payment_url(self, payment, request):
        """Tạo URL thanh toán VNPay"""
        try:
            # Mock mode: Redirect trực tiếp về success
            if self.vnp_mock:
                logger.info(f"MOCK MODE: Skipping VNPay, redirecting to success")
                mock_url = f"{self.vnp_return_url}?vnp_ResponseCode=00&vnp_TxnRef={str(payment.id).replace('-', '')[:8].upper()}&vnp_TransactionNo=MOCK123456&vnp_BankCode=MOCK&vnp_CardType=ATM&vnp_PayDate={timezone.now().strftime('%Y%m%d%H%M%S')}"
                return mock_url
            
            # Tạo order_id ngắn gọn từ payment ID
            order_id = str(payment.id).replace('-', '')[:8].upper()
            
            # Tạo vnp_CreateDate và vnp_ExpireDate theo GMT+7
            create_time = timezone.now().astimezone(timezone.get_fixed_timezone(7*60))
            expire_time = create_time + timedelta(hours=1)
            
            vnp_create_date = create_time.strftime('%Y%m%d%H%M%S')
            vnp_expire_date = expire_time.strftime('%Y%m%d%H%M%S')
            
            # Tạo order_info ngắn gọn
            if payment.booking and payment.booking.court:
                order_info = f'Dat san {payment.booking.court.name}'
            else:
                order_info = f'Thanh toan {order_id}'
            
            # Lấy IP address
            ip_address = self.get_client_ip(request)
            
            # Tạo vnp_Params
            vnp_params = {
                'vnp_Version': self.vnp_version,
                'vnp_Command': self.vnp_command,
                'vnp_TmnCode': self.vnp_tmn_code,
                'vnp_Amount': str(int(payment.amount * 100)),  # VNPay yêu cầu amount * 100
                'vnp_CurrCode': 'VND',
                'vnp_TxnRef': order_id,
                'vnp_OrderInfo': order_info,
                'vnp_OrderType': 'other',
                'vnp_Locale': 'vn',
                'vnp_ReturnUrl': self.vnp_return_url,
                'vnp_IpAddr': ip_address,
                'vnp_CreateDate': vnp_create_date,
                'vnp_ExpireDate': vnp_expire_date,
            }
            
            # Sắp xếp params theo alphabet
            vnp_params = dict(sorted(vnp_params.items()))
            
            # Tạo query string
            query_string = urllib.parse.urlencode(vnp_params)
            
            # Tạo secure hash với HMAC SHA512
            secure_hash = hmac.new(
                self.vnp_secret_key.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            
            # Tạo payment URL
            payment_url = f"{self.vnp_url}?{query_string}&vnp_SecureHash={secure_hash}"
            
            # Lưu thông tin vào payment
            payment.vnpay_txn_ref = order_id
            payment.vnpay_order_info = order_info
            payment.expired_at = timezone.now() + timedelta(hours=1)
            payment.ip_address = ip_address
            payment.save()
            
            logger.info(f"Created VNPay payment URL for payment {payment.id}")
            logger.debug(f"Query string: {query_string}")
            logger.debug(f"Secure hash: {secure_hash}")
            
            return payment_url
            
        except Exception as e:
            logger.error(f"Error creating VNPay payment URL: {str(e)}")
            raise
    
    def verify_payment_response(self, request_params):
        """Xác thực phản hồi từ VNPay"""
        try:
            # Lấy secure hash từ params
            vnp_secure_hash = request_params.get('vnp_SecureHash')
            
            # Tạo dict params không bao gồm secure hash
            params = {}
            for key, value in request_params.items():
                if key.startswith('vnp_') and key != 'vnp_SecureHash':
                    params[key] = value
            
            # Sắp xếp params
            params = dict(sorted(params.items()))
            
            # Tạo query string
            query_string = urllib.parse.urlencode(params)
            
            # Tạo secure hash
            calculated_hash = hmac.new(
                self.vnp_secret_key.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            
            # So sánh hash
            if calculated_hash != vnp_secure_hash:
                logger.error(f"VNPay signature mismatch. Expected: {calculated_hash}, Got: {vnp_secure_hash}")
                return False, "Chữ ký không hợp lệ"
            
            # Kiểm tra response code
            response_code = request_params.get('vnp_ResponseCode')
            if response_code != '00':
                logger.warning(f"VNPay payment failed with code: {response_code}")
                return False, f"Thanh toán thất bại. Mã lỗi: {response_code}"
            
            logger.info(f"VNPay payment verified successfully")
            return True, "Thanh toán thành công"
            
        except Exception as e:
            logger.error(f"Error verifying VNPay response: {str(e)}")
            return False, str(e)
    
    def get_client_ip(self, request):
        """Lấy IP address của client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
