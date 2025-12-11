from __future__ import annotations

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Product


@receiver(post_migrate)
def generate_tags_after_migrate(sender: type[AppConfig], **kwargs: Any) -> None:
    """
    Генерация тегов для товаров после применения миграций.
    Запускается только для приложения `products`.
    """

    # Сигнал вызывается для каждого приложения — фильтруем.
    if sender.label != "products":
        return None

    # Перебираем товары и пересохраняем для автогенерации тегов.
    for product in Product.objects.all():
        # вызывает пересчёт тегов в модели.
        product.save(update_fields=None)

    return None
