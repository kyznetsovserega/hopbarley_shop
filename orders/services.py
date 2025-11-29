from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError

from cart.models import CartItem
from .models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(request, form_data):
    """
    Создаёт заказ на основе корзины текущего пользователя или session_key.

    Функция:
    - Загружает cart-items для session_key
    - Проверяет наличие обязательных данных (full_name, shipping_address)
    - Проверяет остатки на складе (select_for_update)
    - Создаёт Order и OrderItem (snapshot цены)
    - Уменьшает stock товаров
    - Очищает корзину

    Возвращает созданный Order.
    """

    # === SESSION KEY ===
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    # === LOAD CART ITEMS ===
    cart_items = (
        CartItem.objects
        .filter(session_key=session_key)
        .select_related("product")
    )

    if not cart_items.exists():
        raise ValidationError("Корзина пуста.")

    # === VALIDATE FORM FIELDS ===
    required_fields = ["full_name", "shipping_address"]
    for field in required_fields:
        value = form_data.get(field, "").strip()
        if not value:
            raise ValidationError(f"Поле '{field}' обязательно.")

    full_name = form_data.get("full_name", "").strip()
    email = form_data.get("email", "").strip()
    phone = form_data.get("phone", "").strip()
    shipping_address = form_data.get("shipping_address", "").strip()
    comment = form_data.get("comment", "").strip()

    # === SNAPSHOT + STOCK CHECK ===
    """
    select_for_update() блокирует строки product до конца транзакции,
    предотвращая race condition (double-sell).
    """
    total_price = Decimal(0)
    snapshot = []

    for cart_item in cart_items.select_for_update():
        product = cart_item.product
        qty = cart_item.quantity

        if product.stock < qty:
            raise ValidationError(
                f"Недостаточно товара '{product.name}'. "
                f"В наличии: {product.stock}, в корзине: {qty}."
            )

        line_price = product.price
        total_price += line_price * qty

        snapshot.append({
            "product_id": product.id,
            "product": product,
            "qty": qty,
            "price": line_price,
        })

    # === CREATE ORDER ===
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_price=total_price,

        full_name=full_name,
        email=email,
        phone=phone,
        shipping_address=shipping_address,
        comment=comment,

        status="pending",  # лучше использовать Enum: Order.Status.PENDING
    )

    # === CREATE ORDER ITEMS + UPDATE STOCK ====
    for item in snapshot:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["qty"],
            price=item["price"],  # snapshot
        )

        item["product"].stock -= item["qty"]
        item["product"].save(update_fields=["stock"])

    # === CLEAR CART ===
    cart_items.delete()

    return order
