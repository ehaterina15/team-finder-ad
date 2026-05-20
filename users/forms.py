import re

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль',
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Электронная почта')
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль',
    )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'about', 'phone', 'github_url', 'avatar']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if not phone:
            return phone
        if re.match(r'^8\d{10}$', phone):
            phone = '+7' + phone[1:]
        if not re.match(r'^\+7\d{10}$', phone):
            raise ValidationError(
                'Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX'
            )
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Этот номер телефона уже используется')
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url', '')
        if url and 'github.com' not in url:
            raise ValidationError('Ссылка должна вести на GitHub')
        return url


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Текущий пароль'
        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password2'].label = 'Подтверждение нового пароля'