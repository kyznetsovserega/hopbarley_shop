from __future__ import annotations

from typing import Any

import pytest
from cart.utils import merge_session_cart_into_user_cart
from cart.models import CartItem


@pytest.mark.django_db
def test_merge_session_cart_into_user_cart(
    user_fixture: Any,
    product_fixture: Any,
    web_session_key: str,
) -> None:
    """
    Проверяет корректное объединение guest-cart > user-cart.
    """

    # Создаём гостевую корзину
    CartItem.objects.create(
        session_key=web_session_key,
        product=product_fixture,
        quantity=2,
    )

    # Выполняем merge
    merge_session_cart_into_user_cart(
        user_fixture,
        web_session_key,
    )

    # Теперь должна существовать user-cart запись
    merged = CartItem.objects.get(user=user_fixture)
    assert merged.quantity == 2
    assert merged.product == product_fixture

    # session-корзина должна исчезнуть
    assert CartItem.objects.filter(session_key=web_session_key).count() == 0
