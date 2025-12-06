"""
Генерация тегов для товаров после применения миграций.
"""

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Product


@receiver(post_migrate)
def generate_tags_after_migrate(sender, **kwargs):
    if sender.label != "products":
        return

    for product in Product.objects.all():
        product.save()
