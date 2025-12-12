from __future__ import annotations

import graphene
from graphene import ResolveInfo
from graphene_django import DjangoObjectType

from cart.models import CartItem


class CartItemType(DjangoObjectType):
    """
    Один товар в корзине.
    """

    total_price = graphene.String()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "quantity",
        )

    def resolve_total_price(self, info: ResolveInfo) -> str:
        return str(self.total_price)


class CartType(graphene.ObjectType):
    """
    Объект виртуальной корзины (НЕ модель БД).
    """

    items = graphene.List(CartItemType)
    total_quantity = graphene.Int()
    total_price = graphene.String()

    # ↓↓↓ ВАЖНО ↓↓↓

    def resolve_items(self, info: ResolveInfo):
        return self.get_items()

    def resolve_total_quantity(self, info: ResolveInfo) -> int:
        return sum(item.quantity for item in self.get_items())

    def resolve_total_price(self, info: ResolveInfo) -> str:
        return str(self.get_total())
