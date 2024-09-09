from django.urls import path
from . import views

app_name = 'reservation_delivery'

urlpatterns = [
    path('select_delivery_location/', views.select_delivery_location, name='select_delivery_location'),
    path('select_date_time/', views.select_date_time, name='select_date_time'),
    path('select_lockers/', views.select_delivery_locker, name='select_delivery_locker'),
    path('delivery_reservation_complete/', views.delivery_reservation_complete, name='delivery_reservation_complete'),
    path('view_delivery_reservations/', views.view_delivery_reservations, name='view_delivery_reservations'),
]
