# payments/admin.py

from django.contrib import admin
from .models import Payments

# admin.py : 관리자 인터페이스를 통해 각 앱의 모델을 쉽게 확인하고, 데이터를 탐색

@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'reservation', 'amount', 'created_at', 'updated_at')
    search_fields = ('user__username', 'reservation__id')
