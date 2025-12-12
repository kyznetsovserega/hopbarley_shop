import graphene
from cart.services import CartService
from graphql_api.types.cart_types import CartType


class CartQuery(graphene.ObjectType):
    cart = graphene.Field(
        CartType,
        description="Returns current cart (session or user based).",
    )

    def resolve_cart(self, info):
        return CartService(info.context)
