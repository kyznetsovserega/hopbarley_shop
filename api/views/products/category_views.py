from __future__ import annotations

from typing import Any, List, Type

from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from api.serializers.products.category_serializers import CategorySerializer
from products.models import Category


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
    """
    ViewSet для работы с категориями товаров.
    """

    serializer_class: Type[CategorySerializer] = CategorySerializer
    permission_classes: List[type[AllowAny]] = [AllowAny]

    queryset: QuerySet[Category] = (
        Category.objects.all().select_related("parent").prefetch_related("children").order_by("name")
    )

    # ----------------------------------------------------------------------
    # LIST — список категорий
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Получить список категорий",
        description=(
            "Возвращает список всех категорий с одноуровневой структурой.\n\n"
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
            )
        },
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    # ----------------------------------------------------------------------
    # RETRIEVE — категория по ID
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Получить категорию по ID",
        description=("Возвращает данные одной категории.\n\n" "Пример запроса:\n" "`/api/categories/1/`"),
        responses={
            200: OpenApiResponse(
                response=CategorySerializer,
                description="Категория успешно получена.",
            ),
            404: OpenApiResponse(description="Категория не найдена."),
        },
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)
