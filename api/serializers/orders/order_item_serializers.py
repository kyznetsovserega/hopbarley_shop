from __future__ import annotations

from rest_framework import serializers

from orders.models import OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор товарной позиции заказа (snapshot).

    Содержит:
        - имя товара на момент покупки (product_name)
        - изображение товара на момент покупки (product_image)
        - количество (quantity)
        - цена на момент оформления (price)
        - итоговая стоимость позиции (total)
    """

    product_name: serializers.CharField = serializers.CharField(
        source="product.name",
        read_only=True,
        help_text="Название товара на момент покупки.",
    )

    product_image: serializers.ImageField = serializers.ImageField(
        source="product.image",
        read_only=True,
        help_text="Изображение товара на момент покупки.",
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "quantity",
            "price",
            "total",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "product_image",
            "total",
        ]
