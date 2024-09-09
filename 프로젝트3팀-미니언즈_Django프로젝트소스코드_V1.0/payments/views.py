from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Payments, Card
from .forms import PaymentForm, CardAdditionForm
from common.models import Reservations
from datetime import timedelta, datetime
from django.utils.timezone import make_aware, now  # Django의 시간대 인식 유틸리티 사용


# 요금 계산 함수
def calculate_rental_fee(start_datetime, end_datetime, reservation_type, half_hour_rate=500, delivery_fee=3000):
    time_difference = end_datetime - start_datetime
    total_minutes = time_difference.total_seconds() / 60
    total_fee = total_minutes / 30 * half_hour_rate

    if reservation_type == 'delivery':
        total_fee += delivery_fee

    return int(total_fee)

# 카드 추가 뷰
@login_required
def add_card(request):
    if request.method == 'POST':
        form = CardAdditionForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            return redirect('payments:payment_form')
    else:
        form = CardAdditionForm()

    return render(request, 'payments/add_card.html', {'form': form})

@login_required
def payment_form(request):
    user = request.user
    reservation = Reservations.objects.filter(user=user).last()

    start_datetime = reservation.start_datetime
    end_datetime = reservation.end_datetime

    # 시간대 문제가 있을 경우 시간대 인식 객체로 변환
    if not start_datetime.tzinfo:
        start_datetime = make_aware(start_datetime)
    if not end_datetime.tzinfo:
        end_datetime = make_aware(end_datetime)

    # 등록된 카드가 있는지 확인
    registered_cards = Card.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = user
            payment.reservation = reservation
            payment.amount = calculate_rental_fee(reservation.start_datetime, reservation.end_datetime, reservation.reservation_type)
            payment.card = registered_cards.first() if registered_cards.exists() else None
            
            # 폼이 유효하고 결제 정보가 제대로 저장되면 payment_success로 리디렉션
            payment.save()
            return redirect('payments:payment_success')
        else:
            # 폼이 유효하지 않을 경우 폼에 오류 메시지를 전달합니다.
            return render(request, 'payments/payment_form.html', {
                'form': form, 
                'reservation': reservation, 
                'amount': calculate_rental_fee(reservation.start_datetime, reservation.end_datetime, reservation.reservation_type),
                'registered_cards': registered_cards,
                'error_message': '카드를 선택하거나 필수 정보를 입력하세요.'
            })
    else:
        form = PaymentForm()

    return render(request, 'payments/payment_form.html', {
        'form': form, 
        'reservation': reservation, 
        'amount': calculate_rental_fee(reservation.start_datetime, reservation.end_datetime, reservation.reservation_type),
        'registered_cards': registered_cards,
    })


@login_required
def payment_success(request):
    return render(request, 'payments/payment_success.html')
