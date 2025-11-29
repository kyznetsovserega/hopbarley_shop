from __future__ import annotations

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Конфигурация приложения users.

    Подключает signals для автоматического создания профилей
    при создании пользователя.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        # Импорт сигналов при старте приложения
        from . import signals
