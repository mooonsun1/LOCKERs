# common/management/commands/add_locations_and_lockers.py
from django.core.management.base import BaseCommand
from common.models import Locations, Lockers

class Command(BaseCommand):
    help = 'Add predefined locations and lockers'

    def handle(self, *args, **kwargs):
        location_data = {
        '서울시': ['남산타워', '경복궁', '롯데월드', '북촌 한옥마을', '여의도 한강공원', '서울어린이대공원'],
        '부산시': ['송도 해상케이블카', '감천 문화마을', '해운대 해수욕장', '광안리 해수욕장', '해동 용궁사', '오륙도 스카이워크'],
        '제주도': ['카멜리아힐', '휴애리 자연생활공원', '섭지코지', '에코랜드 테마파크', '용두암', '만장굴'],
        '강원도': ['남이섬', '양양 인구해변', '대관령 양떼목장', '속초 해수욕장', '삼척 장호항', '강릉 경포대'],
        '전라남도': ['여수 해상케이블카', '여수 유월드 루지 테마파크', '낭만포차거리', '목포 해상케이블카', '죽녹원', '섬진강 기차마을'],
    }

        for city, districts in location_data.items():
            for district in districts:
                location, created = Locations.objects.get_or_create(city=city, district=district, defaults={
                    'address': f"{city} {district} 주소"
                })
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Location created: {location}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Location already exists: {location}"))

                # 각 위치에 64개의 보관함 생성
                for locker_number in range(1, 65):
                    locker, created = Lockers.objects.get_or_create(locker_number=locker_number, location=location, defaults={
                        'status': 'available'
                    })
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Locker {locker_number} created at {location}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Locker {locker_number} already exists at {location}"))

        self.stdout.write(self.style.SUCCESS('Locations and lockers added successfully.'))
