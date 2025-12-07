from cart.models import CartItem
from django.db import transaction

def merge_session_cart_into_user_cart(user, session_key):
    """
    Переносит товары из корзины гостя (session_key)
    в корзину пользователя (user).

    Если товары одинаковые – складываем quantity.
    """
    if not session_key:
        return

    session_items = CartItem.objects.filter(
        session_key=session_key,
        user__isnull=True
    )

    if not session_items.exists():
        return

    with transaction.atomic():
        for item in session_items:
            existing = CartItem.objects.filter(
                user=user,
                product=item.product
            ).first()

            if existing:
                # товар уже есть > увеличиваем количество
                existing.quantity += item.quantity
                existing.save()
                item.delete()
            else:
                # переносим как новый элемент
                item.user = user
                item.session_key = None
                item.save()
