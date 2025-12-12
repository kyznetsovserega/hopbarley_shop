from __future__ import annotations

import graphene
from graphene import ResolveInfo

from cart.services import CartService
from graphql_api.types.cart_types import CartType
from products.models import Product


class AddToCart(graphene.Mutation):
    """
    Добавить товар в корзину.
    """

    class Arguments:
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=False, default_value=1)

    cart = graphene.Field(CartType)
    error = graphene.String()

    @classmethod
    def mutate(
        cls,
        root,
        info: ResolveInfo,
        product_id: int,
        quantity: int = 1,
    ):
        service = CartService(info.context)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return AddToCart(cart=None, error="Product not found.")

        service.add(product=product, quantity=quantity)
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

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return UpdateCartItem(cart=None, error="Product not found.")

        service.update(product=product, quantity=quantity)
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

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return RemoveFromCart(cart=None, error="Product not found.")

        service.remove(product=product)
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
