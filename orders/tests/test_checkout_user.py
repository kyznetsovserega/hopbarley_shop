from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse

from cart.models import CartItem
from orders.models import Order


@pytest.mark.django_db
def test_authenticated_checkout_uses_user_cart(
    client_web: Any,
    user_fixture: Any,
    product_fixture: Any,
) -> None:
    """
    Проверяет, что авторизованный пользователь оформляет заказ
    из своей user-cart, а не через session_key.
    """

    # Авторизация
    client_web.login(username="testuser", password="testpass123")

    # User-cart
    CartItem.objects.create(
        user=user_fixture,
        product=product_fixture,
        quantity=3,
    )

    # POST checkout
    response = client_web.post(
        reverse("orders:checkout"),
        {
            "full_name": "Auth User",
            "email": "t@t.com",
            "phone": "111",
            "shipping_address": "Street",
            "payment_method": "cod",
        },
    )

    # Должен быть redirect
    assert response.status_code == 302

    # Проверяем заказ
    order: Order | None = Order.objects.first()
    assert order is not None

    assert order.user == user_fixture
    assert order.total_price == product_fixture.price * 3

    # Корзина должна быть очищена
    assert CartItem.objects.count() == 0

    # Stock уменьшен
    product_fixture.refresh_from_db()
    assert product_fixture.stock == 7
