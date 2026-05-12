from django import forms
from django.core.exceptions import ValidationError
import re
from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

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
    email    = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if not phone:
            return phone
        # приводим 8... к +7...
        if re.match(r'^8\d{10}$', phone):
            phone = '+7' + phone[1:]
        if not re.match(r'^\+7\d{10}$', phone):
            raise ValidationError('Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX')
        # проверяем уникальность
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


class ChangePasswordForm(forms.Form):
    old_password  = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        if not self.user.check_password(cleaned.get('old_password', '')):
            raise ValidationError({'old_password': 'Неверный текущий пароль'})
        if cleaned.get('new_password1') != cleaned.get('new_password2'):
            raise ValidationError({'new_password2': 'Пароли не совпадают'})
        return cleaned