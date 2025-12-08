from __future__ import annotations

from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from cart.models import CartItem
from .models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(request, form_data):
    """
    Создаёт заказ на основе корзины текущего пользователя или гостя.

    Поддерживает две корзины:
    - session_key (гости)
    - user (авторизованные)
    """

    # ------------------------------------------------------------
    # 1. Session key
    # ------------------------------------------------------------
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # ------------------------------------------------------------
    # 2. Загрузка корзины (FIX!)
    # ------------------------------------------------------------
    if request.user.is_authenticated:
        cart_items = (
            CartItem.objects
            .filter(user=request.user)
            .select_related("product")
        )
    else:
        cart_items = (
            CartItem.objects
            .filter(session_key=session_key)
            .select_related("product")
        )

    if not cart_items.exists():
        raise ValidationError("Корзина пуста")

    # ------------------------------------------------------------
    # 3. Проверка обязательных полей
    # ------------------------------------------------------------
    required_fields = ["full_name", "shipping_address", "phone"]
    for field in required_fields:
        value = form_data.get(field, "").strip()
        if not value:
            raise ValidationError("Поле обязательно.")

    full_name = form_data["full_name"].strip()
    email = form_data.get("email", "").strip()
    phone = form_data["phone"].strip()
    shipping_address = form_data["shipping_address"].strip()
    comment = form_data.get("comment", "").strip()
    payment_method = form_data.get("payment_method", "cash")

    # ------------------------------------------------------------
    # 4. Валидация телефона
    # ------------------------------------------------------------
    if not phone:
        raise ValidationError("Поле обязательно.")

    # ------------------------------------------------------------
    # 5. Проверка остатков товара + snapshot
    # ------------------------------------------------------------
    total_price = Decimal(0)
    snapshot = []

    for cart_item in cart_items.select_for_update():
        product = cart_item.product
        qty = cart_item.quantity

        if product.stock < qty:
            raise ValidationError("Недостаточно товара")

        snapshot.append({
            "product": product,
            "qty": qty,
            "price": product.price,
        })

        total_price += product.price * qty

    # ------------------------------------------------------------
    # 6. Создание заказа
    # ------------------------------------------------------------
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=session_key,

        full_name=full_name,
        email=email,
        phone=phone,
        shipping_address=shipping_address,
        comment=comment,

        payment_method=payment_method,
        status=Order.STATUS_PENDING,
        total_price=total_price,
    )

    # ------------------------------------------------------------
    # 7. Создание OrderItem + списание stock
    # ------------------------------------------------------------
    for item in snapshot:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["qty"],
            price=item["price"],
        )

        item["product"].stock -= item["qty"]
        item["product"].save(update_fields=["stock"])

    # ------------------------------------------------------------
    # 8. Очистка корзины
    # ------------------------------------------------------------
    cart_items.delete()

    return order
