from __future__ import annotations
from django.apps import AppConfig


class CartConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cart"
    verbose_name = "Корзина"

    def ready(self):
        """
        Метод вызывается при загрузке приложения.
        Оставлен для возможного подключения сигналов (merge корзины, логирование).
        """
        pass
