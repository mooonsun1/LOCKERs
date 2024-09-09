from django.db import models
from django.conf import settings
from common.models import Reservations

# 사용자 카드 정보를 관리하는 모델
class Card(models.Model):
    card_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, unique=True)
    card_expiry = models.CharField(max_length=5)
    card_cvc = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Card'

# 결제 정보를 관리하는 모델
class Payments(models.Model):
    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservations, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, default=None )
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Payments'
