from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse
from django.test import Client

from cart.models import CartItem
from orders.models import Order


# ============================================================================
# 1. SUCCESS CHECKOUT
# ============================================================================

@pytest.mark.django_db
def test_checkout_success(
    product_fixture: Any,
    web_session_key: str,
) -> None:
    client: Client = Client()

    # Передаём session_key через cookie
    client.cookies["sessionid"] = web_session_key

    # Добавляем товар в корзину
    CartItem.objects.create(
        session_key=web_session_key,
        product=product_fixture,
        quantity=2,
    )

    response = client.post(
        reverse("orders:checkout"),
        {
            "full_name": "Tester",
            "email": "a@a.com",
            "phone": "123456",
            "shipping_address": "street 1",
            "payment_method": "cod",
        },
    )

    # Должен быть редирект на success
    assert response.status_code == 302

    order: Order | None = Order.objects.first()
    assert order is not None

    # Проверка итоговой стоимости
    assert order.total_price == product_fixture.price * 2

    assert response.url == reverse(
        "orders:success",
        kwargs={"order_id": order.id},
    )


# ============================================================================
# 2. EMPTY CART
# ============================================================================

@pytest.mark.django_db
def test_checkout_empty_cart(
    web_session_key: str,
) -> None:
    client: Client = Client()
    client.cookies["sessionid"] = web_session_key

    response = client.post(
        reverse("orders:checkout"),
        {
            "full_name": "Tester",
            "email": "a@a.com",
            "phone": "123456",
            "shipping_address": "street 1",
            "payment_method": "cod",
        },
    )

    assert response.status_code == 200
    assert "Корзина пуста" in response.content.decode()


# ============================================================================
# 3. NOT ENOUGH STOCK
# ============================================================================

@pytest.mark.django_db
def test_checkout_not_enough_stock(
    product_fixture: Any,
    web_session_key: str,
) -> None:
    client: Client = Client()
    client.cookies["sessionid"] = web_session_key

    # Маленький остаток
    product_fixture.stock = 1
    product_fixture.save()

    # В корзине quantity=5 — больше, чем stock
    CartItem.objects.create(
        session_key=web_session_key,
        product=product_fixture,
        quantity=5,
    )

    response = client.post(
        reverse("orders:checkout"),
        {
            "full_name": "Tester",
            "email": "a@a.com",
            "phone": "123456",
            "shipping_address": "street 1",
            "payment_method": "cod",
        },
    )

    assert response.status_code == 200
    assert "Недостаточно" in response.content.decode()


# ============================================================================
# 4. MISSING REQUIRED FIELDS
# ============================================================================

@pytest.mark.django_db
def test_checkout_missing_required_fields(
    product_fixture: Any,
    web_session_key: str,
) -> None:
    client: Client = Client()
    client.cookies["sessionid"] = web_session_key

    # Добавляем один товар, чтобы не получить ошибку "Корзина пуста"
    CartItem.objects.create(
        session_key=web_session_key,
        product=product_fixture,
        quantity=1,
    )

    response = client.post(
        reverse("orders:checkout"),
        {
            "full_name": "",
            "shipping_address": "",
            "phone": "",
            "payment_method": "cod",
        },
    )

    # Форма возвращает 200 и текст ошибки
    assert response.status_code == 200
    assert "Поле" in response.content.decode()
