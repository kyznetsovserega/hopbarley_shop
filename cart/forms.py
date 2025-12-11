"""
Формы корзины.

AddToCartForm выполняет валидацию количества:
- значение должно быть >= 1
- значение не может превышать остаток товара (stock)
- учитывает текущее количество товара в корзине (если CartItem уже существует)
"""

from __future__ import annotations

from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from cart.models import CartItem
from products.models import Product


class AddToCartForm(forms.Form):
    """
    Форма добавления товара в корзину.
    """

    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Количество",
        help_text="Сколько единиц товара добавить в корзину.",
    )

    def __init__(
        self,
        *args: Any,
        product: Product,
        request: HttpRequest | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.product = product
        self.request = request

        # МАКСИМУМ динамически ограничиваем stock'ом
        self.fields["quantity"].widget.attrs.update({"max": self.product.stock})

    # -----------------------------------------------------
    # Основная валидация
    # -----------------------------------------------------
    def clean_quantity(self) -> int:
        qty = int(self.cleaned_data.get("quantity", 1))

        if qty < 1:
            raise ValidationError("Количество должно быть не меньше 1.")

        if self.request is None:
            raise ValidationError("Ошибка запроса.")

        # Определяем владельца корзины
        if self.request.user.is_authenticated:
            owner_filter = {"user": self.request.user}
        else:
            session_key = self.request.session.session_key
            owner_filter = {"session_key": session_key}

        # Проверяем, есть ли уже CartItem для этого товара
        existing_item = CartItem.objects.filter(
            product=self.product, **owner_filter
        ).first()

        current_qty = existing_item.quantity if existing_item else 0
        total_qty = current_qty + qty

        # ПРОВЕРКА остатков
        if total_qty > self.product.stock:
            raise ValidationError(f"Доступно только {self.product.stock} шт.")

        return qty
