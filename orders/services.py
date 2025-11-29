from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from cart.models import CartItem
from .models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(request, form_data):

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_items = (
        CartItem.objects
        .filter(session_key=session_key)
        .select_related("product")
    )

    if not cart_items.exists():
        raise ValidationError("Корзина пуста")

    snapshot = []
    total_price = Decimal(0)

    for item in cart_items:
        product = item.product
        qty = item.quantity

        if product.stock < qty:
            raise ValidationError(
                f"Товара '{product.name}' недостаточно. "
                f"Осталось: {product.stock}, в корзине: {qty}"
            )

        snapshot.append((product, qty, product.price))
        total_price += product.price * qty

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_price=total_price,
        full_name=form_data["full_name"],
        email=form_data.get("email", ""),
        phone=form_data.get("phone", ""),
        shipping_address=form_data["shipping_address"],
        comment=form_data.get("comment", ""),
    )

    for product, qty, price in snapshot:
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty,
            price=price,
        )
        product.stock -= qty
        product.save()

    cart_items.delete()

    return order
