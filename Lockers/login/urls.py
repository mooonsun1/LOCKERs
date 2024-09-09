from django.urls import path
from . import views
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth.forms import AuthenticationForm

app_name="login"

urlpatterns = [
    path("create/", views.create, name="create"),
    path('check/username/', views.check_username, name='check_username'),#중복확인
    path("login/", views.user_login, name="login"),  # 로그인
    path("logout" , views.user_logout, name="logout"),
    path("loginhome/", views.loginhome, name="loginhome"), # 로그인 후 홈화면
    path("detail/" , views.detail , name='detail'),  # 회원정보 조회
    path("update/" , views.user_update , name='update'), # 회원정보수정
    path("delete", views.user_delete, name="delete"),  # 회원 삭제 
    path("password_change/" ,views.change_password , name="password_change"), # 비밀번호변경
    path('recovery/', views.RecoveryIdView.as_view(), name='recovery'),
    path('recovery/find/', views.ajax_find_id_view, name='ajax_id'),
    path('recovery/pw/find/', views.AjaxFindPwView.as_view(), name='ajax_pw'),
    path('recovery/pw/', views.PasswordRecoveryView.as_view(), name='recovery_pw'),
    path('recovery/confirm/', views.PasswordRecoveryConfirmView.as_view(), name='password_recovery_confirm'),
    path('reset/', views.PasswordResetView.as_view(), name='password_reset'),
]