from __future__ import annotations

import graphene
from graphene import ResolveInfo

from cart.services import CartService
from graphql_api.types.cart_types import CartType


class AddToCart(graphene.Mutation):
    """
    Добавить товар в корзину.
    """

    class Arguments:
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=False, default_value=1)

    cart = graphene.Field(CartType)

    @classmethod
    def mutate(
        cls,
        root,
        info: ResolveInfo,
        product_id: int,
        quantity: int = 1,
    ):
        service = CartService(info.context)
        service.add(product_id=product_id, quantity=quantity)
        return AddToCart(cart=service)


class UpdateCartItem(graphene.Mutation):
    """
    Изменить количество товара в корзине.
    """

    class Arguments:
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    cart = graphene.Field(CartType)

    @classmethod
    def mutate(
        cls,
        root,
        info: ResolveInfo,
        product_id: int,
        quantity: int,
    ):
        service = CartService(info.context)
        service.update(product_id=product_id, quantity=quantity)
        return UpdateCartItem(cart=service)


class RemoveFromCart(graphene.Mutation):
    """
    Удалить товар из корзины.
    """

    class Arguments:
        product_id = graphene.ID(required=True)

    cart = graphene.Field(CartType)

    @classmethod
    def mutate(
        cls,
        root,
        info: ResolveInfo,
        product_id: int,
    ):
        service = CartService(info.context)
        service.remove(product_id=product_id)
        return RemoveFromCart(cart=service)


class ClearCart(graphene.Mutation):
    """
    Очистить корзину.
    """

    cart = graphene.Field(CartType)

    @classmethod
    def mutate(cls, root, info: ResolveInfo):
        service = CartService(info.context)
        service.clear()
        return ClearCart(cart=service)


class CartMutations(graphene.ObjectType):
    """
    Корневой объект мутаций корзины.
    """

    add_to_cart = AddToCart.Field()
    update_cart_item = UpdateCartItem.Field()
    remove_from_cart = RemoveFromCart.Field()
    clear_cart = ClearCart.Field()
