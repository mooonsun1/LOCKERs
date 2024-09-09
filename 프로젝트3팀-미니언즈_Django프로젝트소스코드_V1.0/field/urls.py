from django.urls import path
from . import views

app_name = 'field'

urlpatterns = [
    path('recognize/', views.recognize_face, name='recognize_face'),  # URL을 recognize로 변경
    path('classify/', views.classify_face_view, name='classify_face'),  # 여기서 함수명을 바꾸지 않도록 수정
    path('map/', views.map_view, name='map'),  # map/ 경로를 추가
    path('get_location_prefix/', views.get_location_prefix, name='get_location_prefix'),
]
