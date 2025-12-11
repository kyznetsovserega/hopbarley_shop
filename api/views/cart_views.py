from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiRequest
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.serializers.cart_serializers import CartItemSerializer
from cart.models import CartItem
from cart.services import CartService


@extend_schema(
    tags=["Cart"],
    summary="Управление корзиной",
    description=(
        "API корзины. Работает для гостей и авторизованных пользователей.\n\n"
        "**Принцип:**\n"
        "- Гость → корзина по session_key\n"
        "- Пользователь → корзина по user.id"
    ),
)
class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]
    lookup_field = "pk"

    # ---------------------------------------------------
    # QUERYSET
    # ---------------------------------------------------
    def get_queryset(self) -> QuerySet[CartItem]:
        service = CartService(self.request)
        return service.get_items_queryset()

    # ---------------------------------------------------
    # LIST
    # ---------------------------------------------------
    @extend_schema(
        summary="Получить содержимое корзины",
        responses={200: CartItemSerializer(many=True)},
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    # ---------------------------------------------------
    # CREATE
    # ---------------------------------------------------
    @extend_schema(
        summary="Добавить товар в корзину",
        request=OpenApiRequest(
            request=dict,
            examples=[
                OpenApiExample(
                    "Добавление",
                    value={"product": 1, "quantity": 2},
                )
            ],
        ),
        responses={
            201: OpenApiResponse(response=CartItemSerializer),
            400: OpenApiResponse(description="Ошибка валидации"),
        },
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        product_id = request.data.get("product")
        quantity_raw = request.data.get("quantity", 1)

        if not product_id:
            return Response({"detail": "Поле 'product' обязательное"}, status=400)

        try:
            quantity: int = int(quantity_raw)
        except Exception:
            return Response({"detail": "Quantity must be a number"}, status=400)

        service = CartService(request)

        try:
            product = service._resolve_product(product_id)
            item = service.add(product, quantity)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=201)

    # ---------------------------------------------------
    # UPDATE
    # ---------------------------------------------------
    @extend_schema(
        summary="Изменить количество товара",
        request=OpenApiRequest(
            request=dict,
            examples=[OpenApiExample("Изменение", value={"quantity": 5})],
        ),
        responses={200: CartItemSerializer, 400: OpenApiResponse()},
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        service = CartService(request)
        item = service._get_cart_item(int(kwargs["pk"]))

        try:
            new_qty = int(request.data.get("quantity"))
        except Exception:
            return Response({"detail": "Quantity must be a number"}, status=400)

        if new_qty < 1:
            return Response({"detail": "Quantity must be >= 1"}, status=400)

        diff: int = new_qty - item.quantity

        try:
            if diff > 0:
                service.add(item.product, diff)
            else:
                for _ in range(abs(diff)):
                    service.decrease(item.id)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)

        item.refresh_from_db()
        return Response(self.get_serializer(item).data)

    # ---------------------------------------------------
    # DELETE (DESTROY)
    # ---------------------------------------------------
    @extend_schema(
        summary="Удалить товар из корзины",
        responses={204: OpenApiResponse(description="Удалено")},
    )
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        service = CartService(request)
        service.remove(int(kwargs["pk"]))
        return Response(status=204)

    # ---------------------------------------------------
    # CLEAR — кастомный метод
    # ---------------------------------------------------
    @extend_schema(
        summary="Очистить корзину",
        responses={200: OpenApiResponse(description="Корзина очищена.")},
    )
    @action(detail=False, methods=["delete"])
    def clear(self, request: Request) -> Response:
        service = CartService(request)
        service.clear()
        return Response({"detail": "Cart cleared"})
