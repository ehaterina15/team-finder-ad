import io
import random
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


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
        return self.create_user(email, name, surname, password, **extra_fields)


class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email      = models.EmailField(unique=True)
    name       = models.CharField(max_length=124)
    surname    = models.CharField(max_length=124)
    avatar     = models.ImageField(upload_to='avatars/', blank=True)
    phone      = models.CharField(max_length=12, blank=True)
    github_url = models.URLField(blank=True)
    about      = models.TextField(max_length=256, blank=True)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    skills     = models.ManyToManyField(Skill, blank=True, related_name='users')

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = self._generate_avatar()
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        COLORS = ['#5B8CFF', '#FF7043', '#66BB6A', '#AB47BC', '#26C6DA']
        size   = 200
        color  = random.choice(COLORS)
        letter = self.name[0].upper() if self.name else '?'

        img  = Image.new('RGB', (size, size), color)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype('arial.ttf', 100)
        except OSError:
            font = ImageFont.load_default(size=100)

        bbox = draw.textbbox((0, 0), letter, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(
            ((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]),
            letter, fill='white', font=font
        )

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return ContentFile(buf.getvalue(), name=f'avatar_{self.email}.png')

    def __str__(self):
        return f'{self.surname} {self.name}'