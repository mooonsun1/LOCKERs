from django import forms
from .models import Users

from django.contrib.auth.forms import UserCreationForm, UserChangeForm , PasswordChangeForm,PasswordResetForm ,SetPasswordForm ,AuthenticationForm

from django.contrib.auth import get_user_model

Users = get_user_model()  # User 모델을 가져오는 함수

class CustomUserCreateForm(UserCreationForm):
    username = forms.CharField(label="아이디", max_length=150)
    password1 = forms.CharField(label='비밀번호', widget=forms.PasswordInput())
    password2 = forms.CharField(label="비밀번호 확인",
                                widget=forms.PasswordInput(),
                                help_text="비밀번호 확인을 위해 이전과 동일한 비밀번호를 입력하세요.")
    phone = forms.CharField(label="전화번호", help_text="'-'는 빼고 입력하세요")

    class Meta:
        model = Users
        fields = ['username', 'password1', 'password2', 'name', 'email', 'phone']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Users.objects.filter(username=username).exists():
            raise forms.ValidationError("이미 사용 중인 아이디입니다.")
        return username

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="사용자 아이디", widget=forms.TextInput(attrs={'autofocus': True}))

class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = Users
        fields = ['username', 'name', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.HiddenInput()

# 사용자 정보 및 비밀번호 변경 폼
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="기존 패스워드",
        widget=forms.PasswordInput()
    )
    new_password1 = forms.CharField(
        label="새 패스워드",
        widget=forms.PasswordInput()
    )
    new_password2 = forms.CharField(
        label="새 패스워드 확인",
        widget=forms.PasswordInput()
    )

# 아이디 찾기 폼 
class RecoveryIdForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput,)
    email = forms.EmailField(widget=forms.EmailInput,)

    class Meta:
        fields = ['name', 'email']

    def __init__(self, *args, **kwargs):
        super(RecoveryIdForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = '이름'
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'id': 'form_name',
        })
        self.fields['email'].label = '이메일'
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'id': 'form_email' 
        })

###### 비밀번호 재설정 form ########




class PasswordRecoveryForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput,)
    name = forms.CharField(widget=forms.TextInput,)
    email = forms.EmailField(widget=forms.EmailInput,)
    
    class Meta:
        model = Users
        fields = ['username', 'name', 'email']

    def __init__(self, *args, **kwargs):
        super(PasswordRecoveryForm, self).__init__(*args, **kwargs)  
        self.fields['username'].label = 'ID'
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'id': 'form_username',
        })
        self.fields['name'].label = '이름'
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'id': 'form_name',
        })
        self.fields['email'].label = '이메일'
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'id': 'form_email' 
        })

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')

        if not Users.objects.filter(username=username, name=name, email=email).exists():
            raise forms.ValidationError("입력한 정보와 일치하는 사용자가 없습니다.")

        return cleaned_data
    
class PasswordResetForm(forms.Form):
    new_password = forms.CharField(
        label="새 비밀번호",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '새 비밀번호를 입력하세요'
        })
    )
    confirm_password = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호를 다시 입력하세요'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return cleaned_data
