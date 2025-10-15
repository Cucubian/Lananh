from django import forms
from .models import ServiceOrder, ServiceOrderItem, Service

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['booking', 'notes']
        widgets = {
            'booking': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ghi chú thêm (nếu có)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['booking'].queryset = user.bookings.filter(status__in=['confirmed', 'pending'])
            self.fields['booking'].required = False

class AddServiceItemForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_available=True),
        label='Dịch vụ',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Số lượng',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
