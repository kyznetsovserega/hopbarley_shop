from __future__ import annotations

from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiRequest,
)

from api.serializers.orders.order_serializers import OrderSerializer
from orders.models import Order
from orders.services import create_order_from_cart


@extend_schema(
    tags=["Orders"],
    summary="Работа с заказами",
    description=(
        "API оформления и просмотра заказов.\n\n"
        "**Особенности:**\n"
        "- Гость может оформить заказ (`POST /api/orders/`).\n"
        "- Авторизованный пользователь может просматривать только свои заказы.\n"
        "- Пользователь НЕ может изменять или удалять заказ через API.\n\n"
        "**Типовые сценарии:**\n"
        "- Оформление заказа через корзину\n"
        "- Просмотр истории заказов\n"
        "- Получение информации о заказе"
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    # ----------------------------------------------------------------------
    # PERMISSIONS
    # ----------------------------------------------------------------------
    def get_permissions(self):
        """
        POST доступен всем (гость может оформить заказ),
        остальные методы доступны только авторизованным пользователям.
        """
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    # ----------------------------------------------------------------------
    # QUERYSET
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Список заказов пользователя",
        description=(
            "Возвращает список заказов текущего пользователя.\n\n"
            "**Гость** > всегда пустой список.\n"
            "**Пользователь** > только его собственные заказы.\n"
        ),
        responses={
            200: OpenApiResponse(
                response=OrderSerializer(many=True),
                description="Список заказов успешно получен.",
            )
        },
    )
    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Order.objects.none()

        return Order.objects.filter(user=user).order_by("-created_at")

    # ----------------------------------------------------------------------
    # RETRIEVE — просмотр конкретного заказа
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Получить заказ по ID",
        description=(
            "Возвращает подробную информацию о заказе.\n\n"
            "**Важно:** пользователь может просматривать только свои заказы.\n"
            "Если он пытается открыть чужой заказ → ошибка 403."
        ),
        responses={
            200: OpenApiResponse(
                response=OrderSerializer,
                description="Информация о заказе успешно получена.",
            ),
            403: OpenApiResponse(
                description="Нет доступа к заказу.",
                examples=[
                    OpenApiExample(
                        "Попытка доступа к чужому заказу",
                        value={"detail": "Вы не можете просматривать этот заказ."},
                    )
                ],
            ),
            404: OpenApiResponse(description="Заказ не найден."),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()

        if order.user != request.user:
            raise PermissionDenied("Вы не можете просматривать этот заказ.")

        return super().retrieve(request, *args, **kwargs)

    # ----------------------------------------------------------------------
    # CREATE — оформление заказа
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Оформить заказ",
        description=(
            "Создаёт заказ на основе корзины.\n\n"
            "**Гость:**\n"
            "- Корзина определяется по `session_key`.\n"
            "- Заказ создаётся без привязки к пользователю.\n\n"
            "**Пользователь:**\n"
            "- Корзина привязана к `user.id`.\n"
            "- Заказ записывается на пользователя.\n\n"
            "**В теле запроса передаются:**\n"
            "- Полное имя (`full_name`)\n"
            "- Email (`email`)\n"
            "- Телефон (`phone`)\n"
            "- Адрес доставки (`shipping_address`)\n"
            "- Способ оплаты (`payment_method`)\n"
            "- Комментарий (опционально)"
        ),
        request=OpenApiRequest(
            request=dict,
            examples=[
                OpenApiExample(
                    "Пример заказа",
                    value={
                        "full_name": "John Smith",
                        "email": "john@example.com",
                        "phone": "+123456789",
                        "shipping_address": "New York, Madison St. 12",
                        "payment_method": "card",
                        "comment": "Позвонить перед доставкой",
                    },
                ),
            ],
        ),
        responses={
            201: OpenApiResponse(
                response=OrderSerializer,
                description="Заказ успешно создан.",
            ),
            400: OpenApiResponse(
                description="Ошибка оформления заказа.",
                examples=[
                    OpenApiExample(
                        "Недостаточно данных",
                        value={"detail": "Не удалось создать заказ."},
                    )
                ],
            ),
        },
    )
    def create(self, request, *args, **kwargs) -> Response:
        try:
            order = create_order_from_cart(request, request.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
