from __future__ import annotations

from typing import Any, TYPE_CHECKING, Optional

from django.db import transaction
from cart.models import CartItem

if TYPE_CHECKING:

    from django.contrib.auth.models import AbstractUser as UserType
else:
    UserType = Any


def merge_session_cart_into_user_cart(
    user: UserType,
    session_key: Optional[str],
) -> None:
    """
    Переносит товары из корзины гостя (session_key)
    в корзину пользователя (user).
    Если товары одинаковые – складываем quantity.
    """

    if not session_key:
        return None

    session_items = CartItem.objects.filter(
        session_key=session_key,
        user__isnull=True,
    )

    if not session_items.exists():
        return None

    with transaction.atomic():
        for item in session_items:
            existing = (
                CartItem.objects.filter(
                    user=user,
                    product=item.product,
                ).first()
            )

            if existing:
                existing.quantity += item.quantity
                existing.save()
                item.delete()
            else:
                item.user = user
                item.session_key = None
                item.save()

    return None
