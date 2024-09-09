from django import forms
from .models import Payments, Card

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payments
        fields = []  # payment_method 필드를 제거했기 때문에 비워둡니다.

class CardAdditionForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['card_number', 'card_expiry', 'card_cvc']
        widgets = {
            'card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Card Number',
                'maxlength': '19',
                'pattern': '[0-9\s]{13,19}',
            }),
            'card_expiry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'MM/YY',
                'maxlength': '5',
                'pattern': '((0[1-9])|(1[0-2]))/([0-9]{2})',
            }),
            'card_cvc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CVC',
                'maxlength': '4',
                'pattern': '[0-9]{3,4}',
            }),
        }

    def clean_card_expiry(self):
        expiry = self.cleaned_data['card_expiry']
        if len(expiry) != 5 or expiry[2] != '/':
            raise forms.ValidationError("MM/YY 형식으로 입력하세요.")
        month, year = expiry.split('/')
        if not (1 <= int(month) <= 12):
            raise forms.ValidationError("유효한 월을 입력하세요.")
        if not (0 <= int(year) <= 99):
            raise forms.ValidationError("유효한 연도를 입력하세요.")
        return expiry

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number'].replace(' ', '')
        if not card_number.isdigit() or len(card_number) not in [13, 15, 16]:
            raise forms.ValidationError("올바른 카드 번호를 입력하세요.")
        return card_number

    def clean_card_cvc(self):
        cvc = self.cleaned_data['card_cvc']
        if not cvc.isdigit() or len(cvc) not in [3, 4]:
            raise forms.ValidationError("유효한 CVC를 입력하세요.")
        return cvc
