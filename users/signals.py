from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created: bool, **kwargs):
    """
    Создаёт профиль сразу после создания пользователя.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance: User, created: bool, **kwargs):
    """
    Сохраняет профиль при обновлении данных пользователя.
    """
    if not created:
        # Профиль гарантированно существует, т.к. создается в create_user_profile
        instance.profile.save()
