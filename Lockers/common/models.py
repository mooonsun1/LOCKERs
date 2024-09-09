from django.db import models
from django.apps import apps
from django.utils import timezone

class Locations(models.Model):
    location_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=100)  # 도시 추가
    district = models.CharField(max_length=100, default="Unknown")  # 구 추가
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Locations'
        unique_together = ('city', 'district')  # 같은 도시와 구 조합이 중복되지 않도록 설정

    def __str__(self):
        return f'{self.city} {self.district}'


class Lockers(models.Model):
    locker_id = models.AutoField(primary_key=True)
    locker_number = models.IntegerField()
    status = models.CharField(max_length=9, blank=True, null=True)
    location = models.ForeignKey(Locations, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'Lockers'


class Reservations(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('login.Users', models.DO_NOTHING, blank=True, null=True)
    start_locker = models.ForeignKey(Lockers, models.DO_NOTHING, blank=True, null=True)
    end_locker = models.ForeignKey(Lockers, models.DO_NOTHING, related_name='reservations_end_locker_set', blank=True, null=True)
    start_location = models.ForeignKey(Locations, models.DO_NOTHING, blank=True, null=True)
    end_location = models.ForeignKey(Locations, models.DO_NOTHING, related_name='reservations_end_location_set', blank=True, null=True)
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9, blank=True, null=True)
    reservation_type = models.CharField(max_length=50, blank=True, null=True)  # 예약 유형 구분 추가
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Reservations'

    def save(self, *args, **kwargs):
        current_time = timezone.now()
        if self.end_datetime > current_time:
            self.status = '사용중'
        else:
            self.status = '사용완료'
        super().save(*args, **kwargs)

    def get_total_amount(self):
        Payments = apps.get_model('payments', 'Payments')
        total_amount = Payments.objects.filter(reservation=self).aggregate(models.Sum('amount'))['amount__sum']
        if total_amount is not None:
            total_amount = int(total_amount)
        return total_amount
