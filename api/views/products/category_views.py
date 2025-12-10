from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
)

from products.models import Category
from api.serializers.products.category_serializers import CategorySerializer


@extend_schema(
    tags=["Categories"],
    summary="Работа с категориями товаров",
    description=(
        "Эндпоинт предоставляет доступ к дереву категорий.\n\n"
        "**Возможности:**\n"
        "- Получение списка категорий\n"
        "- Родительские категории (parent)\n"
        "- Дочерние категории (children)\n\n"
        "Используется:\n"
        "- На странице каталога\n"
        "- В фильтрах по категориям\n"
        "- При отображении информации о товарах"
    ),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    queryset = (
        Category.objects.all()
        .select_related("parent")
        .prefetch_related("children")
        .order_by("name")
    )

    # ----------------------------------------------------------------------
    # LIST endpoint — список категорий
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Получить список категорий",
        description=(
            "Возвращает список всех категорий с одноуровневой деревовидной структурой.\n\n"
            "Каждая категория включает:\n"
            "- `parent`: родитель\n"
            "- `children`: дочерние категории\n\n"
            "Пример использования:\n"
            "`/api/categories/`"
        ),
        responses={
            200: OpenApiResponse(
                response=CategorySerializer(many=True),
                description="Список категорий успешно получен.",
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=[
                            {
                                "id": 1,
                                "name": "Hops",
                                "slug": "hops",
                                "description": "Aroma and bittering hops",
                                "parent": None,
                                "children": [
                                    {
                                        "id": 3,
                                        "name": "Aroma Hops",
                                        "slug": "aroma-hops",
                                    }
                                ]
                            },
                            {
                                "id": 2,
                                "name": "Malt",
                                "slug": "malt",
                                "description": "Base and specialty malts",
                                "parent": None,
                                "children": []
                            }
                        ]
                    )
                ]
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # ----------------------------------------------------------------------
    # RETRIEVE endpoint — получить категорию по ID
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Получить категорию по ID",
        description=(
            "Возвращает данные одной категории.\n\n"
            "Пример запроса:\n"
            "`/api/categories/1/`"
        ),
        responses={
            200: OpenApiResponse(
                response=CategorySerializer,
                description="Категория успешно получена."
            ),
            404: OpenApiResponse(description="Категория не найдена."),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
