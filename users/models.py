from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from .constants import (
    SKILL_NAME_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
    USER_FIRST_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)
from .managers import UserManager
from .utils import generate_avatar


class Skill(models.Model):
    name = models.CharField(
        max_length=SKILL_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Навык',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта',
    )
    name = models.CharField(
        max_length=USER_FIRST_NAME_MAX_LENGTH,
        verbose_name='Имя',
    )
    surname = models.CharField(
        max_length=USER_SURNAME_MAX_LENGTH,
        verbose_name='Фамилия',
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        verbose_name='Аватар',
    )
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        blank=True,
        default='',
        validators=[
            RegexValidator(
                r'^(\+7|8)\d{10}$',
                'Телефон: формат +7XXXXXXXXXX (10 цифр после +7)',
            )
        ],
        verbose_name='Телефон',
    )
    github_url = models.URLField(
        blank=True,
        default='',
        validators=[
            RegexValidator(
                r'^$|^https?://github\.com/',
                'Ссылка должна вести на GitHub',
            )
        ],
        verbose_name='GitHub',
    )
    about = models.TextField(
        max_length=USER_ABOUT_MAX_LENGTH,
        blank=True,
        verbose_name='О себе',
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='users',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = generate_avatar(self.email, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.surname} {self.name}'
