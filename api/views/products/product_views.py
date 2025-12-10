from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from products.models import Product
from api.serializers.products.product_serializers import ProductSerializer


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
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    # Базовый queryset
    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("specifications")
    )

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]

    # Поиск
    search_fields = ["name", "description"]

    # Сортировка
    ordering_fields = ["price", "created_at"]

    # Фильтры
    filterset_fields = {
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
            "**Примеры фильтрации:**\n"
            "- `/api/products/?search=hop`\n"
            "- `/api/products/?ordering=-price`\n"
            "- `/api/products/?category__id=2`\n"
            "- `/api/products/?price__gte=5&price__lte=20`"
        ),
        responses={
            200: OpenApiResponse(
                response=ProductSerializer(many=True),
                description="Список товаров успешно получен.",
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=[
                            {
                                "id": 1,
                                "name": "Citra Hops",
                                "slug": "citra-hops",
                                "short_description": "Aroma hop for IPAs",
                                "description": "Ideal for IPA brewing...",
                                "unit": "kg",
                                "price": "5.99",
                                "old_price": "6.50",
                                "stock": 40,
                                "image": "/media/products/citra.jpg",
                                "is_active": True,
                                "tags": ["aroma", "citra"],
                                "is_discounted": True,
                                "discount_percent": 10,
                                "specifications": [
                                    {"id": 1, "name": "Alpha Acid", "value": "12%"}
                                ],
                                "category": {
                                    "id": 2,
                                    "name": "Hops",
                                    "slug": "hops",
                                    "description": "Aroma and bittering hops",
                                    "parent": None,
                                    "children": [],
                                },
                                "created_at": "2025-01-01T00:00:00Z",
                                "updated_at": "2025-01-01T00:00:00Z",
                            }
                        ],
                    )
                ],
            )
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # ----------------------------------------------------------------------
    # RETRIEVE endpoint
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Детальная информация о товаре",
        description=(
            "Возвращает всю информацию о товаре по его `slug`.\n\n"
            "Пример запроса:\n"
            "`/api/products/citra-hops/`"
        ),
        responses={
            200: OpenApiResponse(
                response=ProductSerializer,
                description="Информация о товаре успешно получена.",
            ),
            404: OpenApiResponse(description="Товар не найден."),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
