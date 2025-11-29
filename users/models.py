from __future__ import annotations

from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Город",
    )

    address = models.TextField(
        blank=True,
        verbose_name="Адрес",
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата рождения",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создан",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлён",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self) -> str:
        username = getattr(self.user, "username", "Unknown")
        return f"Profile of {username}"
