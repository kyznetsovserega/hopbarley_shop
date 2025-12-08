from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance: User, created: bool, **kwargs):
    """
    Создаёт профиль при первом сохранении пользователя.
    Если профиль уже существует — ничего не делает.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Профиль может отсутствовать, если был создан вручную или в тестах
        UserProfile.objects.get_or_create(user=instance)
