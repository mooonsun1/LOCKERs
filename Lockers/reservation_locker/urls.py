from django.urls import path
from . import views

app_name = 'reservation_locker'

urlpatterns = [
    path('select_location/', views.select_location, name='select_location'),
    path('select_date_time/', views.select_date_time, name='select_date_time'),
    path('select_locker/', views.select_locker, name='select_locker'),
    path('locker_reservation_complete/', views.locker_reservation_complete, name='locker_reservation_complete'),
    path('view_locker_reservations/', views.view_locker_reservations, name='view_locker_reservations'),
]
