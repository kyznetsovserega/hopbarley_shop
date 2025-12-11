from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import UserProfile

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as UserType
else:
    UserType = Any

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_profile(
    sender: type[UserType],
    instance: UserType,
    created: bool,
    **kwargs: Any,
) -> None:
    """
    Создаёт профиль при первом сохранении пользователя.
    Если профиль уже существует — гарантируем, что он не будет потерян.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
