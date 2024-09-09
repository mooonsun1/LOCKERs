from django.db import models
from common.models import Reservations, Lockers, Locations
from django.conf import settings

class ReservationDelivery(models.Model):
    reservation = models.OneToOneField(Reservations, on_delete=models.CASCADE, primary_key=True)
    start_location = models.ForeignKey(Locations, related_name='delivery_start_location', on_delete=models.CASCADE)
    end_location = models.ForeignKey(Locations, related_name='delivery_end_location', on_delete=models.CASCADE)
    start_locker = models.ForeignKey(Lockers, related_name='delivery_start_locker', on_delete=models.CASCADE)
    end_locker = models.ForeignKey(Lockers, related_name='delivery_end_locker', on_delete=models.CASCADE, null=True, default=None)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'ReservationDelivery'
