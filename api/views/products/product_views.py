from __future__ import annotations

from typing import Any, List, Type

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from api.serializers.products.product_serializers import ProductSerializer
from products.models import Product


@extend_schema(
    tags=["Products"],
    summary="Получение данных о товарах",
    description=(
        "Эндпоинты для работы с каталогом товаров.\n\n"
        "**Возможности:**\n"
        "- Получение списка товаров\n"
        "- Поиск (`name`, `description`)\n"
        "- Фильтры (category__id, price_gte/lte)\n"
        "- Сортировка (price, created_at)\n"
        "- Детальная страница товара по `slug`\n\n"
        "Возвращаются только активные товары (`is_active=True`)."
    ),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet для модели Product.
    """

    serializer_class: Type[ProductSerializer] = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    # ---- queryset ----
    queryset: QuerySet[Product] = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("specifications")
    )

    # ---- фильтры, сортировка, поиск ----
    filter_backends: List[Any] = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]

    search_fields: List[str] = ["name", "description"]
    ordering_fields: List[str] = ["price", "created_at"]

    filterset_fields: dict[str, List[str]] = {
        "category__id": ["exact"],
        "price": ["gte", "lte"],
    }

    # ----------------------------------------------------------------------
    # LIST endpoint
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Список товаров",
        description=(
            "Возвращает список товаров с поддержкой поиска, сортировки и фильтров.\n\n"
            "**Примеры запросов:**\n"
            "- `/api/products/?search=hop`\n"
            "- `/api/products/?ordering=-price`\n"
            "- `/api/products/?category__id=2`\n"
            "- `/api/products/?price__gte=5&price__lte=20`"
        ),
        responses={
            200: OpenApiResponse(
                response=ProductSerializer(many=True),
                description="Список товаров успешно получен.",
            )
        },
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    # ----------------------------------------------------------------------
    # RETRIEVE endpoint
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Детальная информация о товаре",
        description=(
            "Возвращает всю информацию о товаре по его `slug`.\n\n"
            "Пример: `/api/products/citra-hops/`"
        ),
        responses={
            200: OpenApiResponse(
                response=ProductSerializer,
                description="Информация о товаре успешно получена.",
            ),
            404: OpenApiResponse(description="Товар не найден."),
        },
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)
