from __future__ import annotations

from decimal import Decimal

import graphene
from graphene_django import DjangoObjectType

from orders.models import Order, OrderItem


class OrderItemType(DjangoObjectType):
    """
    Товарная позиция в заказе.

    Содержит:
    - product — товар
    - quantity — количество
    - price — цена за единицу на момент покупки (snapshot)
    - total — итог по позиции (price * quantity)
    """

    total = graphene.Decimal(
        description="Total price for this item (quantity x price)."
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "quantity",
            "price",
            "total",
        )
        description = "Single product position inside an order."

    def resolve_total(self, info: graphene.ResolveInfo) -> Decimal:
        return self.price * self.quantity  # type: ignore[no-any-return]


class OrderType(DjangoObjectType):
    """
    Заказ пользователя (или гостя).

    Содержит:
    - статус, способ оплаты
    - сумму заказа
    - контактные данные и адрес
    - связанные позиции (items)
    - вычисляемое поле items_count
    """

    items_count = graphene.Int(
        description="Total quantity of products across all items in the order."
    )

    class Meta:
        model = Order
        fields = (
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
            "updated_at",
            "items",
            "items_count",
            "user",
        )
        description = "Order entity with customer, pricing and items information."

    def resolve_items_count(self, info: graphene.ResolveInfo) -> int:
        # Используем уже готовое свойство модели
        return self.items_count  # type: ignore[no-any-return]
