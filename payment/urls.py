from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    # Payment Method Selection
    path('method/<int:booking_id>/', views.payment_method_selection, name='payment_method_selection'),
    
    # VNPay Payment
    path('vnpay/create/<int:booking_id>/', views.create_vnpay_payment, name='create_vnpay_payment'),
    path('vnpay/payment/<uuid:payment_id>/', views.vnpay_payment, name='vnpay_payment'),
    path('vnpay-return/', views.vnpay_return, name='vnpay_return'),
    path('vnpay-ipn/', views.vnpay_ipn, name='vnpay_ipn'),
    
    # Payment Management
    path('detail/<uuid:payment_id>/', views.payment_detail, name='payment_detail'),
    path('list/', views.payment_list, name='payment_list'),
    path('cancel/<uuid:payment_id>/', views.cancel_payment, name='cancel_payment'),
    path('retry/<uuid:payment_id>/', views.retry_payment, name='retry_payment'),
    
    # Result Pages
    path('success/<uuid:payment_id>/', views.payment_success, name='payment_success'),
    path('failed/<uuid:payment_id>/', views.payment_failed, name='payment_failed'),
    
    # API
    path('api/status/<uuid:payment_id>/', views.payment_status_api, name='payment_status_api'),
]
