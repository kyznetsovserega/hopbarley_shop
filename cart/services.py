"""
Сервисный слой корзины.

Отвечает за бизнес-логику:
- добавление товара
- увеличение/уменьшение количества
- удаление и очистку
- получение содержимого корзины
- проверку остатков (stock)
- поддержку двух режимов владения: user и session_key
"""

from __future__ import annotations

from typing import Iterable, Dict, Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from cart.models import CartItem
from products.models import Product


class CartService:
    """
    Унифицированный сервис корзины.

    Логика:
    - Если пользователь авторизован > владелец = user
    - Если нет > владелец = session_key
    - Для каждого товара существует только один CartItem
    """

    def __init__(self, request):
        self.request = request

        # Гарантируем наличие session_key
        if not request.session.session_key:
            request.session.create()

        self.session_key = request.session.session_key
        self.user = request.user if request.user.is_authenticated else None

    # ---------------------------------------------
    # Вспомогательные методы
    # ---------------------------------------------
    def _owner_filter(self) -> Dict[str, Any]:
        """Возвращает фильтр для выборки cart-items."""
        if self.user:
            return {"user": self.user}
        return {"session_key": self.session_key}

    def _get_cart_item(self, item_id: int) -> CartItem:
        """Возвращает CartItem владельца или ошибку."""
        return CartItem.objects.get(id=item_id, **self._owner_filter())

    def _resolve_product(self, product_id: int) -> Product:
        """Возвращает продукт по ID или 404 (для API ViewSet)."""
        return get_object_or_404(Product, id=product_id)

    # ---------------------------------------------
    # Публичные методы сервиса
    # ---------------------------------------------
    def get_items(self) -> Iterable[CartItem]:
        """Получить все элементы корзины текущего владельца."""
        return CartItem.objects.filter(**self._owner_filter()).select_related("product")

    def get_items_queryset(self):
        """
        Метод нужен только для API.
        Возвращает QuerySet корзины текущего владельца.
        """
        return CartItem.objects.filter(**self._owner_filter()).select_related("product")

    def get_total(self):
        """Посчитать итоговую сумму корзины."""
        return sum(item.total_price for item in self.get_items())

    @transaction.atomic
    def add(self, product: Product, quantity: int):
        """
        Добавляет товар в корзину.
        - Если CartItem существует > увеличивает quantity
        - Если нет > создаёт новую запись
        """
        owner = self._owner_filter()

        item, created = CartItem.objects.select_for_update().get_or_create(
            product=product,
            defaults={"quantity": quantity, **owner},
            **owner
        )

        if not created:
            new_qty = item.quantity + quantity
            if new_qty > product.stock:
                raise ValidationError("Недостаточно товара на складе.")
            item.quantity = new_qty
            item.save()

        return item

    @transaction.atomic
    def increase(self, item_id: int):
        item = self._get_cart_item(item_id)

        if item.quantity + 1 > item.product.stock:
            raise ValidationError("Недостаточно товара на складе.")

        item.quantity += 1
        item.save()

    @transaction.atomic
    def decrease(self, item_id: int):
        item = self._get_cart_item(item_id)

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    def remove(self, item_id: int):
        """Удаление товара из корзины."""
        self._get_cart_item(item_id).delete()

    def clear(self):
        """Очистка корзины владельца."""
        CartItem.objects.filter(**self._owner_filter()).delete()
