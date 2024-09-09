from django.db import models
from common.models import Reservations, Lockers, Locations
from django.conf import settings

class ReservationLocker(models.Model):
    reservation = models.OneToOneField(Reservations, on_delete=models.CASCADE, primary_key=True)
    locker = models.ForeignKey(Lockers, on_delete=models.CASCADE)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'ReservationLocker'
