"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.views.generic import TemplateView
from login.views import loginhome  # 홈 뷰 임포트
from login import views as login_views
from django.conf.urls.static import static
from field import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('', login_views.start, name='start'),  # 시작화면 URL
    path("login/", include("login.urls")),
    path("", TemplateView.as_view(template_name = "home.html"), name="home"),
    path('home/', login_views.loginhome, name='loginhome'),  # 홈 페이지 경로
    path('accounts/profile/', loginhome),  # 로그인 후 리디렉션 경로 설정
    path('reservation_locker/', include('reservation_locker.urls')),
    path('reservation_delivery/', include('reservation_delivery.urls')),
    path("", TemplateView.as_view(template_name = "home.html"), name="home"),
    path('faces/', include('faces.urls')),
    path('field/', include('field.urls')),
    path('payments/', include('payments.urls')),
    path('map/', views.map_view, name='map'),  # '/map' 경로를 직접 연결
    
]

from django.conf.urls.static import static
from config import settings

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

