"""
Сериализатор корзины.

Включает:
- данные товара
- текущую цену товара
- итоговую цену позиции (total_price)
"""

from __future__ import annotations

from rest_framework import serializers
from cart.models import CartItem


class CartSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(
        source="product.name",
        read_only=True,
        help_text="Название товара."
    )

    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True,
        help_text="Цена товара."
    )

    total_price = serializers.SerializerMethodField(
        help_text="Итоговая стоимость (количество * цена)."
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "product_title",
            "product_price",
            "total_price",
        ]

    def get_total_price(self, obj):
        """Возвращает итоговую стоимость позиции."""
        return obj.product.price * obj.quantity
