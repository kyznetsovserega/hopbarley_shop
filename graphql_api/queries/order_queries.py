from __future__ import annotations

from typing import List, Optional

import graphene
from django.db.models import QuerySet, Sum
from graphene import ResolveInfo

from graphql_api.types.order_types import OrderType
from graphql_api.types.product_types import ProductType
from orders.models import Order, OrderItem
from products.models import Product


class OrderQuery(graphene.ObjectType):
    """
    GraphQL-запросы по заказам и аналитике.

    Включает:
    - order(id): получить конкретный заказ
    - myOrders: заказы текущего пользователя
    - totalRevenue: суммарная выручка (по оплаченным/доставленным)
    - ordersCount: количество всех заказов
    - topProducts(limit): топ товаров по количеству проданных единиц
    """

    order = graphene.Field(
        OrderType,
        id=graphene.Int(required=True),
        description="Returns a single order by its ID.",
    )

    my_orders = graphene.List(
        OrderType,
        description="Returns list of orders for the authenticated user.",
    )

    total_revenue = graphene.Float(description="Total revenue for paid / shipped / delivered orders.")

    orders_count = graphene.Int(description="Total number of orders in the system.")

    top_products = graphene.List(
        ProductType,
        limit=graphene.Int(required=False, default_value=5),
        description="Top products by total sold quantity.",
    )

    # ============================================================
    # RESOLVERS
    # ============================================================

    def resolve_order(self, info: ResolveInfo, id: int) -> Optional[Order]:
        """
        Возвращает заказ по его ID.
        """
        try:
            return Order.objects.select_related("user").prefetch_related("items__product").get(id=id)
        except Order.DoesNotExist as exc:  # pragma: no cover
            raise ValueError(f"Order with ID {id} not found.") from exc

    def resolve_my_orders(self, info: ResolveInfo) -> QuerySet[Order]:
        """
        Возвращает заказы текущего авторизованного пользователя.
        Если пользователь не авторизован — бросает ошибку.
        """
        user = info.context.user

        if not user or not user.is_authenticated:
            raise ValueError("Authentication required to access orders.")

        return Order.objects.filter(user=user).prefetch_related("items__product").order_by("-created_at")

    def resolve_total_revenue(self, info: ResolveInfo) -> float:
        """
        Суммарная выручка по заказам со статусами:
        paid, shipped, delivered.
        """
        result = Order.objects.filter(
            status__in=(
                Order.STATUS_PAID,
                Order.STATUS_SHIPPED,
                Order.STATUS_DELIVERED,
            )
        ).aggregate(total=Sum("total_price"))
        total = result.get("total") or 0
        return float(total)

    def resolve_orders_count(self, info: ResolveInfo) -> int:
        """
        Общее количество заказов.
        """
        return Order.objects.count()

    def resolve_top_products(
        self,
        info: ResolveInfo,
        limit: int = 5,
    ) -> List[Product]:
        """
        Топ товаров по количеству проданных единиц (OrderItem.quantity).

        Возвращает список Product в порядке убывания продаж.
        """
        items = OrderItem.objects.values("product").annotate(total_sold=Sum("quantity")).order_by("-total_sold")[:limit]

        product_ids: List[int] = [obj["product"] for obj in items]
        products: QuerySet[Product] = Product.objects.filter(id__in=product_ids)

        # Сохраняем порядок по агрегату total_sold
        product_map = {p.id: p for p in products}
        ordered_products: List[Product] = [product_map[pid] for pid in product_ids if pid in product_map]
        return ordered_products
