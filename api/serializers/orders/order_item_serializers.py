from __future__ import annotations

from rest_framework import serializers

from orders.models import OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор товарной позиции заказа (snapshot).

    Содержит:
        - имя товара на момент покупки (product_name)
        - изображение товара (product_image)
        - количество единиц (quantity)
        - цена товара на момент оформления (price)
        - итоговая стоимость позиции (price × quantity) (total)

    Используется в составе OrderSerializer для отображения состава заказа.
    """

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
        help_text="Название товара на момент покупки.",
    )

    product_image = serializers.ImageField(
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
