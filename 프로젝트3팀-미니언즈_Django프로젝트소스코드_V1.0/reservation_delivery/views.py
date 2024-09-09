from django.shortcuts import render, redirect
from .models import ReservationDelivery
from common.models import Reservations, Locations, Lockers
from django.utils.dateparse import parse_datetime
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import pytz

@login_required
def select_delivery_location(request):
    if request.method == 'POST':
        start_city = request.POST.get('start_city')
        start_district = request.POST.get('start_district')
        end_city = request.POST.get('end_city')
        end_district = request.POST.get('end_district')

        if start_city and start_district and end_city and end_district:
            start_location = Locations.objects.filter(city=start_city, district=start_district).first()
            end_location = Locations.objects.filter(city=end_city, district=end_district).first()

            if start_location and end_location:
                request.session['start_location_id'] = start_location.location_id
                request.session['end_location_id'] = end_location.location_id

                return redirect('reservation_delivery:select_date_time')

    locations = {
        '서울시': ['남산타워', '경복궁', '롯데월드', '북촌 한옥마을', '여의도 한강공원', '서울어린이대공원'],
        '부산시': ['송도 해상케이블카', '감천 문화마을', '해운대 해수욕장', '광안리 해수욕장', '해동 용궁사', '오륙도 스카이워크'],
        '제주도': ['카멜리아힐', '휴애리 자연생활공원', '섭지코지', '에코랜드 테마파크', '용두암', '만장굴'],
        '강원도': ['남이섬', '양양 인구해변', '대관령 양떼목장', '속초 해수욕장', '삼척 장호항', '강릉 경포대'],
        '전라남도': ['여수 해상케이블카', '여수 유월드 루지 테마파크', '낭만포차거리', '목포 해상케이블카', '죽녹원', '섬진강 기차마을'],
    }

    return render(request, 'reservation_delivery/select_delivery_location.html', {'locations': locations})

@login_required
def select_date_time(request):
    if request.method == 'POST':
        start_datetime_str = request.POST.get('start_datetime')
        end_datetime_str = request.POST.get('end_datetime')

        # 터미널에 입력된 시간 출력
        print(f"Received start_datetime_str: {start_datetime_str}")
        print(f"Received end_datetime_str: {end_datetime_str}")

        # 전달된 ISO 문자열을 파싱하여 timezone-aware datetime 객체로 변환
        start_datetime = parse_datetime(start_datetime_str)
        end_datetime = parse_datetime(end_datetime_str)

        if start_datetime is None or end_datetime is None:
            return render(request, 'reservation_delivery/select_date_time.html', {
                'error': '잘못된 날짜 및 시간 형식입니다.'
            })

        # 만약 파싱된 시간이 timezone-aware하지 않다면, Asia/Seoul로 make_aware
        if timezone.is_naive(start_datetime):
            seoul_tz = pytz.timezone('Asia/Seoul')
            start_datetime = timezone.make_aware(start_datetime, seoul_tz)
        if timezone.is_naive(end_datetime):
            seoul_tz = pytz.timezone('Asia/Seoul')
            end_datetime = timezone.make_aware(end_datetime, seoul_tz)

        # 터미널에 변환된 시간 출력
        print(f"start_datetime (aware): {start_datetime}")
        print(f"end_datetime (aware): {end_datetime}")

        # UTC로 변환하여 세션에 저장
        start_datetime_utc = start_datetime.astimezone(timezone.utc)
        end_datetime_utc = end_datetime.astimezone(timezone.utc)

        # UTC로 변환된 시간 출력
        print(f"start_datetime (UTC): {start_datetime_utc}")
        print(f"end_datetime (UTC): {end_datetime_utc}")

        request.session['start_datetime'] = start_datetime_utc.isoformat()
        request.session['end_datetime'] = end_datetime_utc.isoformat()

        return redirect('reservation_delivery:select_delivery_locker')
    return render(request, 'reservation_delivery/select_date_time.html')

@login_required
def select_delivery_locker(request):
    start_location_id = request.session.get('start_location_id')
    end_location_id = request.session.get('end_location_id')
    start_datetime_str = request.session.get('start_datetime')
    end_datetime_str = request.session.get('end_datetime')

    if not start_location_id or not end_location_id or not start_datetime_str or not end_datetime_str:
        return redirect('reservation_delivery:select_date_time')

    start_datetime = parse_datetime(start_datetime_str)
    end_datetime = parse_datetime(end_datetime_str)

    if request.method == 'POST':
        start_locker_id = request.POST.get('start_locker_id')
        end_locker_id = request.POST.get('end_locker_id')

        # POST 데이터가 제대로 전달되었는지 확인
        print("Start Location ID:", start_location_id)
        print("End Location ID:", end_location_id)
        print("Start Locker ID:", start_locker_id)
        print("End Locker ID:", end_locker_id)

        if not (start_location_id and start_locker_id and end_location_id and end_locker_id):
            return render(request, 'reservation_delivery/select_lockers.html', {
                'error': '모든 보관함과 위치를 선택해야 합니다.'
            })

        start_location = Locations.objects.get(pk=start_location_id)
        end_location = Locations.objects.get(pk=end_location_id)
        start_locker = Lockers.objects.get(pk=start_locker_id)
        end_locker = Lockers.objects.get(pk=end_locker_id)

        # 예약 생성 및 저장
        reservation = Reservations.objects.create(
            user=request.user,
            start_location=start_location,
            end_location=end_location,
            start_locker=start_locker,
            end_locker=end_locker,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status='reserved',
            reservation_type='delivery'
        )
        reservation.save()

        # ReservationDelivery 생성 및 저장
        ReservationDelivery.objects.create(
            reservation=reservation,
            start_location=start_location,
            end_location=end_location,
            start_locker=start_locker,
            end_locker=end_locker,
            delivery_fee=3000.00,
            user=request.user
        )

        return redirect('reservation_delivery:delivery_reservation_complete')

    start_lockers = Lockers.objects.filter(location_id=start_location_id)
    reserved_start_lockers = Reservations.objects.filter(
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
        start_location_id=start_location_id
    ).values_list('start_locker_id', flat=True)

    start_locker_statuses = [
        (locker, 'occupied' if locker.locker_id in reserved_start_lockers else 'available')
        for locker in start_lockers
    ]

    end_lockers = Lockers.objects.filter(location_id=end_location_id)
    reserved_end_lockers = Reservations.objects.filter(
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
        end_location_id=end_location_id
    ).values_list('end_locker_id', flat=True)

    end_locker_statuses = [
        (locker, 'occupied' if locker.locker_id in reserved_end_lockers else 'available')
        for locker in end_lockers
    ]

    context = {
        'start_datetime': start_datetime,
        'end_datetime': end_datetime,
        'start_locker_statuses': start_locker_statuses,
        'end_locker_statuses': end_locker_statuses,
        'start_location_id': start_location_id,
        'end_location_id': end_location_id,
    }

    return render(request, 'reservation_delivery/select_lockers.html', context)



@login_required
def delivery_reservation_complete(request):
    reservation = Reservations.objects.filter(user=request.user).last()

    if reservation is None:
        return render(request, 'reservation_delivery/delivery_reservation_complete.html', {
            'error': '예약된 정보가 없습니다.'
        })

    return render(request, 'reservation_delivery/delivery_reservation_complete.html', {
        'reservation': reservation,
    })

def view_delivery_reservations(request):
    current_time = timezone.now()
    reservations = Reservations.objects.filter(user=request.user, reservation_type='delivery').order_by('-created_at')
    seoul_tz = pytz.timezone('Asia/Seoul')

    for reservation in reservations:
        # 현지 시간대로 변환하여 표시
        reservation.start_datetime = reservation.start_datetime.astimezone(seoul_tz)
        reservation.end_datetime = reservation.end_datetime.astimezone(seoul_tz)

        if reservation.end_datetime > current_time:
            reservation.status = '사용중'
        else:
            reservation.status = '사용완료'
        reservation.save()

    return render(request, 'reservation_delivery/delivery_list.html', {'reservations': reservations, 'current_time': current_time})
