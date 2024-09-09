from django import forms
from .models import ReservationLocker

class LockerReservationForm(forms.ModelForm):
    class Meta:
        model = ReservationLocker
        fields = ['locker', 'start_datetime', 'end_datetime']
