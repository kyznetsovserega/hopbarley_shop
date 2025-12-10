from __future__ import annotations

from django.core.exceptions import ValidationError
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiRequest,
)

from api.serializers.cart_serializers import CartItemSerializer
from cart.services import CartService


@extend_schema(
    tags=["Cart"],
    summary="Управление корзиной",
    description=(
        "API корзины. Работает для гостей и авторизованных пользователей.\n\n"
        "**Как определяется корзина:**\n"
        "- Гость > корзина по `session_key`.\n"
        "- Авторизованный пользователь > корзина по `user.id`.\n\n"
        "CartService автоматически выбирает нужный тип корзины."
    ),
)
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "pk"

    # ----------------------------------------------------------------------
    # LIST
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Получить содержимое корзины",
        description=(
            "Возвращает список товарных позиций корзины.\n\n"
            "Корзина может быть гостевой (session) или пользовательской."
        ),
        responses={200: CartItemSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        service = CartService(self.request)
        return service.get_items_queryset()

    # ----------------------------------------------------------------------
    # CREATE — добавить товар
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Добавить товар в корзину",
        description=(
            "Добавляет товар в корзину.\n\n"
            "**Правила:**\n"
            "- Если товар уже есть в корзине > количество увеличивается.\n"
            "- Количество должно быть ≥ 1.\n"
            "- Ошибка, если товар не найден или количество неверно."
        ),
        request=OpenApiRequest(
            request=dict,  # ← исправлено
            examples=[
                OpenApiExample(
                    "Пример запроса",
                    value={"product": 1, "quantity": 2},
                )
            ],
        ),
        responses={
            201: OpenApiResponse(
                response=CartItemSerializer,
                description="Товар успешно добавлен в корзину.",
                examples=[
                    OpenApiExample(
                        "Успешный ответ",
                        value={
                            "id": 12,
                            "product": 1,
                            "product_title": "Citra Hops",
                            "product_price": "5.99",
                            "quantity": 2,
                            "total_price": "11.98",
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Ошибка валидации.",
                examples=[
                    OpenApiExample(
                        "Ошибка",
                        value={"detail": "Поле 'product' является обязательным."},
                    )
                ],
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response({"detail": "Поле 'product' является обязательным."}, status=400)

        try:
            quantity = int(quantity)
        except Exception:
            return Response({"detail": "Quantity must be a number"}, status=400)

        service = CartService(request)

        try:
            product = service._resolve_product(product_id)
            item = service.add(product, quantity)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(self.get_serializer(item).data, status=201)

    # ----------------------------------------------------------------------
    # UPDATE — изменить количество
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Изменить количество товара в корзине",
        description=(
            "Обновляет количество товара.\n\n"
            "**Правила:**\n"
            "- Количество должно быть ≥ 1.\n"
            "- Ошибка, если количество неверное или товар отсутствует."
        ),
        request=OpenApiRequest(
            request=dict,  # ← исправлено
            examples=[
                OpenApiExample(
                    "Пример запроса",
                    value={"quantity": 5},
                )
            ],
        ),
        responses={
            200: OpenApiResponse(
                response=CartItemSerializer,
                description="Количество обновлено.",
            ),
            400: OpenApiResponse(
                description="Ошибка данных.",
                examples=[
                    OpenApiExample(
                        "Ошибка",
                        value={"detail": "Quantity must be >= 1"},
                    )
                ],
            ),
        },
    )
    def update(self, request, *args, **kwargs):
        service = CartService(request)
        item = service._get_cart_item(kwargs["pk"])

        try:
            new_qty = int(request.data.get("quantity"))
        except Exception:
            return Response({"detail": "Quantity must be a number"}, status=400)

        if new_qty < 1:
            return Response({"detail": "Quantity must be >= 1"}, status=400)

        diff = new_qty - item.quantity

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

    # ----------------------------------------------------------------------
    # DESTROY — удалить позицию
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Удалить товар из корзины",
        description="Удаляет товарную позицию из корзины пользователя или гостя.",
        responses={204: OpenApiResponse(description="Товар удалён из корзины.")},
    )
    def destroy(self, request, *args, **kwargs):
        service = CartService(request)
        service.remove(kwargs["pk"])
        return Response(status=204)

    # ----------------------------------------------------------------------
    # CLEAR — очистить корзину
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Очистить корзину",
        description="Удаляет все позиции из корзины.",
        responses={200: OpenApiResponse(description="Корзина очищена.")},
    )
    @action(detail=False, methods=["delete"])
    def clear(self, request):
        service = CartService(request)
        service.clear()
        return Response({"detail": "Cart cleared"})
