from __future__ import annotations

from typing import Any, Dict, List

from rest_framework import serializers

from orders.models import Order
from .order_item_serializers import OrderItemSerializer


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор заказа.

    Используется для:
        - отображения информации о заказе
        - формирования структуры заказа при его создании

    Включает snapshot-данные товарных позиций (OrderItem).
    """

    # Вложенный список позиций заказа
    items: List[Dict[str, Any]] = OrderItemSerializer(
        many=True,
        read_only=True,
        help_text="Список товарных позиций, входящих в заказ.",
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "payment_method",
            "total_price",
            "shipping_address",
            "full_name",
            "email",
            "phone",
            "comment",
            "created_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "status",          # Меняется только через бизнес-логику
            "total_price",     # Расчётная сумма заказа
            "created_at",      # Дата оформления
            "items",           # Snapshot позиций
        ]
