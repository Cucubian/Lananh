from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, ServiceOrder, ServiceOrderItem
from .forms import ServiceOrderForm, AddServiceItemForm

def service_list(request):
    services = Service.objects.filter(is_available=True)
    category = request.GET.get('category')
    if category:
        services = services.filter(category=category)
    
    return render(request, 'services/service_list.html', {'services': services})

@login_required
def service_order_create(request):
    if request.method == 'POST':
        form = ServiceOrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.save()
            messages.success(request, 'Tạo đơn hàng thành công! Hãy thêm dịch vụ vào đơn.')
            return redirect('services:service_order_detail', pk=order.pk)
    else:
        form = ServiceOrderForm(user=request.user)
    
    return render(request, 'services/service_order_create.html', {'form': form})

@login_required
def service_order_list(request):
    if request.user.is_customer:
        orders = ServiceOrder.objects.filter(customer=request.user)
    else:
        orders = ServiceOrder.objects.all()
    
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'services/service_order_list.html', {'orders': orders})

@login_required
def service_order_detail(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk)
    
    # Check permissions
    if request.user.is_customer and order.customer != request.user:
        messages.error(request, 'Bạn không có quyền xem đơn hàng này.')
        return redirect('services:service_order_list')
    
    return render(request, 'services/service_order_detail.html', {'order': order})

@login_required
def service_order_add_item(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk, customer=request.user)
    
    if order.status not in ['pending', 'processing']:
        messages.error(request, 'Không thể thêm dịch vụ vào đơn hàng này.')
        return redirect('services:service_order_detail', pk=pk)
    
    if request.method == 'POST':
        form = AddServiceItemForm(request.POST)
        if form.is_valid():
            service = form.cleaned_data['service']
            quantity = form.cleaned_data['quantity']
            
            # Check stock
            if service.stock < quantity:
                messages.error(request, 'Không đủ hàng trong kho.')
                return redirect('services:service_order_add_item', pk=pk)
            
            # Check if item already exists
            existing_item = order.items.filter(service=service).first()
            if existing_item:
                existing_item.quantity += quantity
                existing_item.save()
            else:
                ServiceOrderItem.objects.create(
                    order=order,
                    service=service,
                    quantity=quantity
                )
            
            # Update stock
            service.stock -= quantity
            service.save()
            
            messages.success(request, 'Đã thêm dịch vụ vào đơn hàng.')
            return redirect('services:service_order_detail', pk=pk)
    else:
        form = AddServiceItemForm()
    
    return render(request, 'services/service_order_add_item.html', {'form': form, 'order': order})

@login_required
def service_order_remove_item(request, pk, item_id):
    order = get_object_or_404(ServiceOrder, pk=pk, customer=request.user)
    item = get_object_or_404(ServiceOrderItem, pk=item_id, order=order)
    
    if request.method == 'POST':
        # Return stock
        service = item.service
        service.stock += item.quantity
        service.save()
        
        item.delete()
        order.calculate_total()
        messages.success(request, 'Đã xóa dịch vụ khỏi đơn hàng.')
        return redirect('services:service_order_detail', pk=pk)
    
    return render(request, 'services/service_order_remove_item.html', {'order': order, 'item': item})
