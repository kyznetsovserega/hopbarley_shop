from __future__ import annotations

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Конфигурация приложения users.
    Подключает сигнал создания профиля при создании пользователя.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self) -> None:
        # Импорт сигналов при старте приложения
        import users.signals
