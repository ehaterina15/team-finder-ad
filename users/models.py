import io
import random

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_COLORS,
    AVATAR_SIZE,
    SKILL_NAME_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
    USER_FIRST_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, surname, password, **extra_fields)


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
            self.avatar = self._generate_avatar()
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        color = random.choice(AVATAR_COLORS)
        letter = self.name[0].upper() if self.name else '?'

        img = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), color)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype('arial.ttf', 100)
        except OSError:
            font = ImageFont.load_default(size=100)

        bbox = draw.textbbox((0, 0), letter, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(
            ((AVATAR_SIZE - w) / 2 - bbox[0], (AVATAR_SIZE - h) / 2 - bbox[1]),
            letter,
            fill='white',
            font=font,
        )

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return ContentFile(buf.getvalue(), name=f'avatar_{self.email}.png')

    def __str__(self):
        return f'{self.surname} {self.name}'