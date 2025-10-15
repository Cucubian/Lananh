from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('courts/', views.court_list, name='court_list'),
    path('create/', views.booking_create, name='booking_create'),
    path('create/<int:court_id>/', views.booking_create, name='booking_create_court'),
    path('list/', views.booking_list, name='booking_list'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/upload-payment/', views.booking_upload_payment, name='booking_upload_payment'),
    path('<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
]
