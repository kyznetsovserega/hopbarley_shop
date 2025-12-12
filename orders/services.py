from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, TypedDict

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest

from cart.models import CartItem

from .models import Order, OrderItem


class SnapshotItem(TypedDict):
    """Типизированная структура для снимка корзины перед созданием заказа."""

    product: Any
    qty: int
    price: Decimal


@transaction.atomic
def create_order_from_cart(
    request: HttpRequest,
    form_data: Dict[str, Any],
) -> Order:
    """
    Создаёт заказ на основе корзины пользователя.

    Этапы:
    1. Получение session_key.
    2. Загрузка корзины (для анонимных — по session_key).
    3. Валидация формы.
    4. Проверка остатков и создание snapshot данных.
    5. Определение статуса заказа.
    6. Создание Order и OrderItem.
    7. Списание товара.
    8. Очистка корзины.

    Возвращает:
        Order — созданный объект заказа.

    Исключения:
        ValidationError — если корзина пуста или недостаточно товара.
    """

    # ---------------------------
    # 1. Session key
    # ---------------------------
    if request.session.get("session_key") is None:
        request.session.save()
    session_key: str = request.session.session_key

    # ---------------------------
    # 2. Загрузка корзины
    # ---------------------------
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user).select_related("product")
    else:
        cart_items = CartItem.objects.filter(session_key=session_key).select_related("product")

    if not cart_items.exists():
        raise ValidationError("Корзина пуста")

    # ---------------------------
    # 3. Извлечение данных формы
    # ---------------------------
    full_name: str = form_data["full_name"].strip()
    email: str = form_data.get("email", "").strip()
    phone: str = form_data["phone"].strip()
    shipping_address: str = form_data["shipping_address"].strip()
    comment: str = form_data.get("comment", "").strip()
    payment_method: str = form_data.get("payment_method", "cash")

    # ---------------------------
    # 4. Проверка остатков
    # ---------------------------
    total_price: Decimal = Decimal(0)
    snapshot: List[SnapshotItem] = []

    for cart_item in cart_items.select_for_update():
        product = cart_item.product
        qty: int = cart_item.quantity

        if product.stock < qty:
            raise ValidationError("Недостаточно товара")

        snapshot.append(
            SnapshotItem(
                product=product,
                qty=qty,
                price=product.price,
            )
        )

        total_price += product.price * qty

    # ---------------------------
    # 5. Определение статуса
    # ---------------------------
    status: str
    if payment_method == "card":
        status = Order.STATUS_PENDING_PAYMENT
    else:
        status = Order.STATUS_PENDING

    # ---------------------------
    # 6. Создание заказа
    # ---------------------------
    order: Order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=session_key,
        full_name=full_name,
        email=email,
        phone=phone,
        shipping_address=shipping_address,
        comment=comment,
        payment_method=payment_method,
        status=status,
        total_price=total_price,
    )

    # ---------------------------
    # 7. Создание OrderItem
    # ---------------------------
    for item in snapshot:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["qty"],
            price=item["price"],
        )

    # ---------------------------
    # 8. Списание товара
    # ---------------------------
    for item in snapshot:
        product = item["product"]
        product.stock -= item["qty"]
        product.save(update_fields=["stock"])

    # ---------------------------
    # 9. Очистка корзины
    # ---------------------------
    cart_items.delete()

    return order
