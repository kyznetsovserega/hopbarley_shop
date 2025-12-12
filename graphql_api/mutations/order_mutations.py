from __future__ import annotations

from typing import Any, Dict

import graphene
from graphene import ResolveInfo
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from orders.models import Order
from orders.services import create_order_from_cart
from graphql_api.types.order_types import OrderType


class CreateOrderInput(graphene.InputObjectType):
    """
    Входные данные для создания заказа через GraphQL.

    Названия полей в snake_case:
    - full_name -> fullName
    - shipping_address -> shippingAddress
    """
    full_name = graphene.String(required=True)
    email = graphene.String(required=False)
    phone = graphene.String(required=True)
    shipping_address = graphene.String(required=True)
    comment = graphene.String(required=False)
    payment_method = graphene.String(required=True)


class CreateOrderPayload(graphene.Mutation):
    """
    Мутация создания заказа на основе текущей корзины.

    Логика полностью переиспользует сервис `create_order_from_cart`.
    """

    class Arguments:
        data = CreateOrderInput(required=True)

    ok = graphene.Boolean()
    order = graphene.Field(OrderType)
    error = graphene.String()

    @staticmethod
    def mutate(
        root: object,
        info: ResolveInfo,
        data: Dict[str, Any],
    ) -> "CreateOrderPayload":
        request: HttpRequest = info.context  # Django HttpRequest

        try:
            order: Order = create_order_from_cart(request, data)
            return CreateOrderPayload(ok=True, order=order, error=None)
        except ValidationError as exc:
            return CreateOrderPayload(ok=False, order=None, error=str(exc))
        except Exception:
            # В реальном продакшене здесь можно логировать traceback
            return CreateOrderPayload(
                ok=False,
                order=None,
                error="Ошибка оформления заказа. Попробуйте позднее.",
            )


class OrderMutations(graphene.ObjectType):
    """
    Корневые мутации для работы с заказами.

    Сейчас:
    - create_order: создать заказ из корзины
    """

    create_order = CreateOrderPayload.Field(
        description="Creates an order from the current cart and returns it."
    )
