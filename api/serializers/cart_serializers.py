from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from cart.models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор элемента корзины.

    Выводит:
        - товар
        - количество
        - цену товара
        - итоговую стоимость (price * quantity)
    """

    product_title = serializers.CharField(
        source="product.name",
        read_only=True,
        help_text="Название товара.",
    )

    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True,
        help_text="Цена товара за единицу.",
    )

    total_price = serializers.SerializerMethodField(
        help_text="Итоговая стоимость позиции."
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
        read_only_fields = [
            "product_title",
            "product_price",
            "total_price",
        ]

    def get_total_price(self, obj: CartItem) -> Decimal:
        """
        Возвращает итоговую стоимость позиции (Decimal).

        Формула:
            price * quantity
        """
        return obj.product.price * obj.quantity
