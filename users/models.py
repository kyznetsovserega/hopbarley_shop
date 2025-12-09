from __future__ import annotations

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


class UserProfile(models.Model):
    """
    Профиль пользователя.

    Дополняет встроенную модель User контактной информацией,
    адресом и датой рождения. Создаётся автоматически
    через signals.py.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
        db_index=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон",
        validators=[
            RegexValidator(
                regex=r"^[0-9+\-() ]*$",
                message="Телефон может содержать только цифры и символы + - ( )",
            )
        ],
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
        return f"Profile of {self.user.email or self.user.username}"

    def get_full_address(self) -> str:
        """Возвращает форматированный адрес."""
        parts = [self.city, self.address]
        return ", ".join(p for p in parts if p)


