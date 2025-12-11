from __future__ import annotations

from typing import Any

import pytest
from orders.models import Order, OrderItem


# ============================================================================
# ORDER CREATION
# ============================================================================
@pytest.mark.django_db
def test_order_creation(
    order_fixture: Any,
    user_fixture: Any,
) -> None:
    """
    Проверяет корректное создание заказа (Order).
    """
    order = order_fixture

    assert isinstance(order, Order)
    assert order.user == user_fixture
    assert order.status == "pending"
    assert order.shipping_address == "Тестовый адрес"
    assert order.total_price == 0  # из фикстуры
    assert order.items.count() == 0  # OrderItem ещё нет


# ============================================================================
# ORDER ITEM CREATION
# ============================================================================
@pytest.mark.django_db
def test_order_item_creation(
    order_item_fixture: Any,
    product_fixture: Any,
    order_fixture: Any,
) -> None:
    """
    Проверяет корректное создание OrderItem и связи:
    - Order > Items
    - Product > OrderItems
    """
    item = order_item_fixture

    assert isinstance(item, OrderItem)
    assert item.order == order_fixture
    assert item.product == product_fixture
    assert item.quantity == 2
    assert item.price == product_fixture.price

    # Проверка связи "Order > OrderItem"
    assert order_fixture.items.count() == 1

    # Проверка связи "Product > OrderItem"
    assert product_fixture.order_items.count() == 1
