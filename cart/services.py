"""
Сервисный слой корзины.

Отвечает за бизнес-логику:
- добавление товара
- увеличение/уменьшение количества
- удаление и очистку
- получение содержимого корзины
- проверку остатков
- поддержку user/session_key
"""

from __future__ import annotations

from typing import Iterable, Dict, Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from cart.models import CartItem
from products.models import Product


class CartService:
    """
    Унифицированный сервис корзины.

    Логика:
    - Если пользователь авторизован > владельцем считается user
    - Иначе > session_key
    """

    def __init__(self, request: HttpRequest) -> None:
        self.request = request

        # Гарантируем наличие session_key
        if not request.session.session_key:
            request.session.create()

        self.session_key: str = request.session.session_key
        self.user = request.user if request.user.is_authenticated else None

    # ---------------------------------------------
    # Вспомогательные методы
    # ---------------------------------------------
    def _owner_filter(self) -> Dict[str, Any]:
        """Фильтр для выборки CartItem владельца."""
        if self.user:
            return {"user": self.user}
        return {"session_key": self.session_key}

    def _get_cart_item(self, item_id: int) -> CartItem:
        """Получить CartItem владельца или ошибку."""
        return CartItem.objects.get(id=item_id, **self._owner_filter())

    def _resolve_product(self, product_id: int) -> Product:
        """Получить продукт по ID или 404 (для API ViewSet)."""
        return get_object_or_404(Product, id=product_id)

    # ---------------------------------------------
    # Публичные методы сервиса
    # ---------------------------------------------
    def get_items(self) -> Iterable[CartItem]:
        """Возвращает все элементы корзины текущего владельца."""
        return (
            CartItem.objects.filter(**self._owner_filter())
            .select_related("product")
        )

    def get_items_queryset(self) -> QuerySet[CartItem]:
        """
        Метод нужен только для API (DRF ViewSet).
        Возвращает QuerySet корзины текущего владельца.
        """
        return (
            CartItem.objects.filter(**self._owner_filter())
            .select_related("product")
        )

    def get_total(self) -> float:
        """Посчитать итоговую сумму корзины."""
        return float(sum(item.total_price for item in self.get_items()))

    @transaction.atomic
    def add(self, product: Product, quantity: int) -> CartItem:
        """
        Добавление товара в корзину.
        - Если CartItem существует > увеличить количество
        - Если нет > создать новую запись
        """
        owner = self._owner_filter()

        item, created = CartItem.objects.select_for_update().get_or_create(
            product=product,
            defaults={"quantity": quantity, **owner},
            **owner,
        )

        if not created:
            new_qty = item.quantity + quantity
            if new_qty > product.stock:
                raise ValidationError("Недостаточно товара на складе.")
            item.quantity = new_qty
            item.save()

        return item

    @transaction.atomic
    def increase(self, item_id: int) -> None:
        """Увеличить количество на 1."""
        item = self._get_cart_item(item_id)

        if item.quantity + 1 > item.product.stock:
            raise ValidationError("Недостаточно товара на складе.")

        item.quantity += 1
        item.save()

    @transaction.atomic
    def decrease(self, item_id: int) -> None:
        """
        Уменьшить количество на 1.
        Если количество становится 0 — удаляем позицию.
        """
        item = self._get_cart_item(item_id)

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    def remove(self, item_id: int) -> None:
        """Удаление товара из корзины."""
        self._get_cart_item(item_id).delete()

    def clear(self) -> None:
        """Очистка корзины владельца полностью."""
        CartItem.objects.filter(**self._owner_filter()).delete()
