from django import forms
from .models import Booking, Court, TimeSlot
from datetime import date

class BookingForm(forms.ModelForm):
    court = forms.ModelChoiceField(
        queryset=Court.objects.filter(is_active=True),
        label='Chọn sân',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    date = forms.DateField(
        label='Ngày đặt',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'min': date.today().isoformat()
        })
    )
    time_slots = forms.ModelMultipleChoiceField(
        queryset=TimeSlot.objects.all(),
        label='Khung giờ',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'mr-2'
        })
    )
    
    class Meta:
        model = Booking
        fields = ['court', 'date', 'time_slots', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ghi chú thêm (nếu có)'
            })
        }

class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['payment_proof']
        widgets = {
            'payment_proof': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'accept': 'image/*'
            })
        }
