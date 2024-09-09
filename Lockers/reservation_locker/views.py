from django.shortcuts import render, redirect
from .models import ReservationLocker
from common.models import Reservations, Locations, Lockers
from django.utils.dateparse import parse_datetime
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import pytz

@login_required
def select_location(request):
    if request.method == 'POST':
        selected_city = request.POST.get('selected_city')
        selected_district = request.POST.get('selected_district')

        if selected_city and selected_district:
            location = Locations.objects.filter(city=selected_city, district=selected_district).first()
            if location:
                request.session['selected_location_id'] = location.location_id
                return redirect('reservation_locker:select_date_time')

    locations = {
        '서울시': ['남산타워', '경복궁', '롯데월드', '북촌 한옥마을', '여의도 한강공원', '서울어린이대공원'],
        '부산시': ['송도 해상케이블카', '감천 문화마을', '해운대 해수욕장', '광안리 해수욕장', '해동 용궁사', '오륙도 스카이워크'],
        '제주도': ['카멜리아힐', '휴애리 자연생활공원', '섭지코지', '에코랜드 테마파크', '용두암', '만장굴'],
        '강원도': ['남이섬', '양양 인구해변', '대관령 양떼목장', '속초 해수욕장', '삼척 장호항', '강릉 경포대'],
        '전라남도': ['여수 해상케이블카', '여수 유월드 루지 테마파크', '낭만포차거리', '목포 해상케이블카', '죽녹원', '섬진강 기차마을'],
    }

    return render(request, 'reservation_locker/select_location.html', {'locations': locations})

import logging

logger = logging.getLogger(__name__)

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
            return render(request, 'reservation_locker/select_date_time.html', {
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

        return redirect('reservation_locker:select_locker')
    return render(request, 'reservation_locker/select_date_time.html')

@login_required
def select_locker(request):
    location_id = request.session.get('selected_location_id')
    start_datetime_str = request.session.get('start_datetime')
    end_datetime_str = request.session.get('end_datetime')

    if not location_id or not start_datetime_str or not end_datetime_str:
        return redirect('reservation_locker:select_date_time')

    # UTC로 저장된 시간을 파싱
    start_datetime = timezone.datetime.fromisoformat(start_datetime_str)
    end_datetime = timezone.datetime.fromisoformat(end_datetime_str)

    # UTC에서 Asia/Seoul 시간대로 변환
    seoul_tz = pytz.timezone('Asia/Seoul')
    start_datetime_seoul = start_datetime.astimezone(seoul_tz)
    end_datetime_seoul = end_datetime.astimezone(seoul_tz)

    lockers = Lockers.objects.filter(location_id=location_id)
    reserved_lockers = Reservations.objects.filter(
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
        start_location_id=location_id,
        end_location_id=location_id
    ).values_list('start_locker_id', flat=True)

    available_lockers = lockers.exclude(locker_id__in=reserved_lockers)

    locker_statuses = [
        (locker, 'occupied' if locker.locker_id in reserved_lockers else 'available')
        for locker in lockers
    ]

    if request.method == 'POST':
        selected_locker = request.POST.get('selected_locker')
        reservation = Reservations.objects.create(
            user=request.user,
            start_locker_id=selected_locker,
            end_locker_id=selected_locker,
            start_location_id=location_id,
            end_location_id=location_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status='reserved',
            reservation_type='locker'
        )
        reservation.save()

        ReservationLocker.objects.create(
            reservation=reservation,
            locker_id=selected_locker,
            location_id=location_id,
            user=request.user
        )
        return redirect('reservation_locker:locker_reservation_complete')

    context = {
        'start_datetime': start_datetime_seoul,
        'end_datetime': end_datetime_seoul,
        'locker_statuses': locker_statuses,
    }
    return render(request, 'reservation_locker/select_locker.html', context)


@login_required
def locker_reservation_complete(request):
    reservation = Reservations.objects.filter(user=request.user).last()

    if reservation is None:
        return render(request, 'reservation_locker/locker_reservation_complete.html', {
            'error': '예약된 정보가 없습니다.'
        })

    return render(request, 'reservation_locker/locker_reservation_complete.html', {
        'reservation': reservation,
    })

def view_locker_reservations(request):
    current_time = timezone.now()
    reservations = Reservations.objects.filter(user=request.user, reservation_type='locker').order_by('-created_at')
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
    return render(request, 'reservation_locker/locker_list.html', {'reservations': reservations, 'current_time': current_time})
