from django.urls import path
from . import views

app_name = 'faces'

urlpatterns = [
    path('register/', views.register_face, name='register_face'),
    
]
