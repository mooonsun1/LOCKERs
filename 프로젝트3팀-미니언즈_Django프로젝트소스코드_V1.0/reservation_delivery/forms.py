from django import forms
from .models import ReservationDelivery

class DeliveryReservationForm(forms.ModelForm):
    class Meta:
        model = ReservationDelivery
        fields = ['start_location', 'end_location', 'start_datetime', 'end_datetime', 'start_locker', 'end_locker', 'reservation']
