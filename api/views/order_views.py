from __future__ import annotations

from typing import Any, Dict, List, Type

from django.db.models import QuerySet
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiRequest,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from api.serializers.orders.order_serializers import OrderSerializer
from orders.models import Order
from orders.services import create_order_from_cart


@extend_schema(
    tags=["Orders"],
    summary="Работа с заказами",
    description=(
        "API оформления и просмотра заказов.\n\n"
        "**Особенности:**\n"
        "- Гость может оформить заказ (`POST`).\n"
        "- Авторизованный пользователь может просматривать только свои заказы.\n"
        "- Редактирование/удаление заказа запрещены.\n"
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для оформления заказов и просмотра истории заказов.
    """

    serializer_class: Type[OrderSerializer] = OrderSerializer

    # ----------------------------------------------------------------------
    # PERMISSIONS
    # ----------------------------------------------------------------------
    def get_permissions(self) -> List[permissions.BasePermission]:
        """
        POST доступен всем (гость может оформить заказ),
        остальное — только авторизованным пользователям.
        """
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    # ----------------------------------------------------------------------
    # QUERYSET — только свои заказы
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Список заказов пользователя",
        description=(
            "Возвращает список заказов текущего пользователя.\n"
            "- Гость > пустой список\n"
            "- Пользователь > только его собственные\n"
        ),
        responses={
            200: OpenApiResponse(
                response=OrderSerializer(many=True),
                description="Список заказов успешно получен.",
            )
        },
    )
    def get_queryset(self) -> QuerySet[Order]:
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
            "Возвращает информацию о заказе.\n\n"
            "Пользователь может смотреть только свои заказы.\n"
            "Чужой заказ > 403."
        ),
        responses={
            200: OpenApiResponse(
                response=OrderSerializer,
                description="Информация о заказе.",
            ),
            403: OpenApiResponse(
                description="Нет доступа.",
                examples=[
                    OpenApiExample(
                        "Чужой заказ",
                        value={"detail": "Вы не можете просматривать этот заказ."},
                    )
                ],
            ),
            404: OpenApiResponse(description="Не найден."),
        },
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        order: Order = self.get_object()

        if order.user_id != request.user.id:
            raise PermissionDenied("Вы не можете просматривать этот заказ.")

        return super().retrieve(request, *args, **kwargs)

    # ----------------------------------------------------------------------
    # CREATE — оформление заказа
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Оформить заказ",
        description=(
            "Создаёт заказ на основе корзины (гостевой или пользовательской).\n\n"
            "**В запросе:** full_name, email, phone, shipping_address, payment_method, comment\n"
        ),
        request=OpenApiRequest(
            request=Dict[str, Any],
            examples=[
                OpenApiExample(
                    "Пример",
                    value={
                        "full_name": "John Smith",
                        "email": "john@example.com",
                        "phone": "+123456789",
                        "shipping_address": "New York, Madison St. 12",
                        "payment_method": "card",
                        "comment": "Позвонить перед доставкой",
                    },
                )
            ],
        ),
        responses={
            201: OpenApiResponse(
                response=OrderSerializer,
                description="Заказ успешно создан.",
            ),
            400: OpenApiResponse(description="Ошибка оформления заказа."),
        },
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            order: Order = create_order_from_cart(request, request.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
