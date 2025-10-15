from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('order/create/', views.service_order_create, name='service_order_create'),
    path('order/list/', views.service_order_list, name='service_order_list'),
    path('order/<int:pk>/', views.service_order_detail, name='service_order_detail'),
    path('order/<int:pk>/add-item/', views.service_order_add_item, name='service_order_add_item'),
    path('order/<int:pk>/remove-item/<int:item_id>/', views.service_order_remove_item, name='service_order_remove_item'),
]
