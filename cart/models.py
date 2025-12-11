from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

from products.models import Product

User = get_user_model()


class CartItem(models.Model):
    """
    Элемент корзины.

    Поддерживает два режима:
    - Пользовательская корзина (user)
    - Гостевая корзина (session_key)

    Для каждого товара может существовать только одна запись
    на одного владельца (пользователь или гость).
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items",
        null=True,
        blank=True,
        help_text="Владелец корзины. Null — если корзина гостевая.",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        help_text="Товар, добавленный в корзину.",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Количество товара. Минимум 1.",
    )

    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Сессионный ключ гостевой корзины.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product",
            ),
            models.UniqueConstraint(
                fields=["session_key", "product"],
                name="unique_session_product",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self) -> Decimal:
        """Возвращает итоговую стоимость позиции."""
        return self.product.price * self.quantity
