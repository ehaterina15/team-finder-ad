from django.conf import settings
from django.db import models

from .constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_CHOICES,
    PROJECT_STATUS_OPEN,
)


class Project(models.Model):
    name = models.CharField(
        max_length=PROJECT_NAME_MAX_LENGTH,
        verbose_name='Название',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Владелец',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    github_url = models.URLField(
        blank=True,
        verbose_name='GitHub ссылка',
    )
    status = models.CharField(
        max_length=max(len(k) for k, _ in PROJECT_STATUS_CHOICES),
        choices=PROJECT_STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
        verbose_name='Статус',
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participated_projects',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name