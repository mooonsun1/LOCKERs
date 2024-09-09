# payments/urls.py

from django.urls import path
from . import views

# urls.py : URL 경로와 뷰 함수를 매핑
# 각 URL 패턴이 어떤 뷰를 호출하는지, 동적 URL 매개변수는 무엇인지 확인

app_name = 'payments'

urlpatterns = [
    path('payment_form/', views.payment_form, name='payment_form'),
    path('add_card/', views.add_card, name='add_card'),
    path('payment_success/', views.payment_success, name='payment_success'),

]
