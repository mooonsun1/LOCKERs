from django.shortcuts import render , redirect
from django.urls import reverse
from .models import Users


from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreateForm , CustomAuthenticationForm

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash

from .forms import RecoveryIdForm
from django.views.generic import View
from django.http import HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder

from django.views import View
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages

from .forms import PasswordRecoveryForm, PasswordResetForm

from django.http import JsonResponse

import logging
from django.contrib.auth import get_user_model

Users = get_user_model()  # User 모델을 가져오는 함수
# Create your views here.

def create(request):
    if request.method == 'GET':
        return render(
            request,
            "login/create.html",
            {"form":CustomUserCreateForm()}
        )
    elif request.method == "POST":
        form = CustomUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
    
            return redirect(reverse('home'))
        else:
            return render(request, "login/create.html",{"form":form})
        
def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': Users.objects.filter(username=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = '이미 사용 중인 아이디입니다.'
    return JsonResponse(data)

def user_login(request):
    if request.method == "GET":
        return render(request,
                      'login/login.html',
                      {'form': CustomAuthenticationForm()})
    elif request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(reverse('login:loginhome'))
        else:
            return render(
                request,
                'login/login.html',
                {'form': form,
                 "errorMessage": "ID나 Password를 다시 확인하세요."}
            )
        
@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse("home"))

@login_required
def loginhome(request):
    if request.method =="GET":
        return render(request,'login/loginhome.html')

@login_required
def user_update(request):
    if request.method == "GET":
        form = CustomUserChangeForm(instance = request.user)
        return render(request, "login/update.html", {"form":form})
    elif request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance = request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request , user)
            return redirect(reverse('login:detail'))
        else:
            return render(request, "login/update.html", {"from" : form})
        
@login_required
def detail(request):
    user = Users.objects.get(pk=request.user.pk)
    return render(request, "login/detail.html", {"object":user})

from django.contrib import messages
from .forms import CustomUserChangeForm, CustomPasswordChangeForm

@login_required
def change_password(request):
    if request.method == "GET":
        form = CustomPasswordChangeForm(request.user)
        return render(
            request , "login/password_change.html",
            {"form":form}
        )
    elif request.method == "POST":
        form = CustomPasswordChangeForm(request.user , request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(reverse("login:detail"))
        else :
            return render(
                request , 'login/password_change.html',
                {'form':form  , 'errorMessage' : '패스워드를 다시 입력하세요.'}
            )


#######id 찾기 ###########



class RecoveryIdView(View):
    template_name = 'login/user_base.html'
    form_class = RecoveryIdForm

    def get(self, request):
        if request.method=='GET':
            form = self.form_class()
        return render(request, self.template_name, { 'form_pw':form, })


def ajax_find_id_view(request):
    name = request.POST.get('name')
    email = request.POST.get('email')

    # 디버깅을 위해 name과 email 값을 출력
    print(f"Received name: {name}, email: {email}")
    
    try:
        result_id = Users.objects.get(name__iexact=name, email__iexact=email)
    except Users.DoesNotExist:
        print(f"No user found with name: {name} and email: {email}")
        return HttpResponse(json.dumps({"error": "User not found"}, cls=DjangoJSONEncoder), content_type="application/json", status=404)
    
    return HttpResponse(json.dumps({"result_id": result_id.username}, cls=DjangoJSONEncoder), content_type="application/json")

######### 비밀번호 재설정 ##########
class PasswordRecoveryView(View):
    template_name = 'login/password_recovery.html'

    def get(self, request):
        form = PasswordRecoveryForm()
        return render(request, self.template_name, {'form': form})

    # post 메서드를 제거하여 모든 POST 요청을 AjaxFindPwView로 처리
    
class AjaxFindPwView(View):
    def post(self, request):
        form = PasswordRecoveryForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']

            try:
                user = Users.objects.get(username=username, name=name, email=email)
            except Users.DoesNotExist:
                return JsonResponse({'error': '입력하신 정보와 일치하는 사용자가 없습니다.'}, status=400, content_type="application/json")

            # 인증 코드 생성 및 저장
            auth_code = get_random_string(length=6, allowed_chars='0123456789')
            request.session['auth_code'] = auth_code
            request.session['username'] = username

            # 이메일 전송
            subject = "비밀번호 재설정 인증 코드"
            message = render_to_string('login/auth_email.html', {
                'auth_code': auth_code,
                'user': user,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            return JsonResponse({'message': '이메일로 인증코드를 발송하였습니다.'}, status=200, content_type="application/json")
            
        return JsonResponse({'error': '유효하지 않은 입력입니다.'}, status=400, content_type="application/json")



class PasswordRecoveryConfirmView(View):
    template_name = 'login/password_recovery_confirm.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        auth_code = request.POST.get('auth_code')
        username = request.session.get('username')

        try:
            user = Users.objects.get(username=username)
        except Users.DoesNotExist:
            messages.error(request, "유효하지 않은 사용자입니다.")
            return redirect('login:password_recovery')

        if request.session.get('auth_code') == auth_code:
            request.session['user_reset'] = username
            return redirect('login:password_reset')
        else:
            messages.error(request, "인증 코드가 올바르지 않습니다.")
            return render(request, self.template_name)
        
class PasswordResetView(View):
    template_name = 'login/password_reset_form.html'

    def get(self, request):
        if not request.session.get('user_reset'):
            return redirect('login:password_recovery')

        form = PasswordResetForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not request.session.get('user_reset'):
            return redirect('login:password_recovery')

        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user = Users.objects.get(username=request.session['user_reset'])

            user.set_password(new_password)
            user.save()

            messages.success(request, "비밀번호가 성공적으로 변경되었습니다.")
            del request.session['user_reset']
            return redirect('login:login')

        return render(request, self.template_name, {'form': form})

###### 탈퇴

@login_required
def user_delete(request):
    request.user.delete()
    logout(request)
    return redirect(reverse('home'))