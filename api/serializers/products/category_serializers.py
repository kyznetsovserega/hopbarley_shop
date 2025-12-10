from __future__ import annotations

from typing import Any

from rest_framework import serializers

from products.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Category.

    Формирует:
        - сведения о родительской категории (parent)
        - список дочерних категорий первого уровня (children)

    Реализация исключает рекурсивную вложенность.
    """

    parent = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "children",
        ]

    def get_parent(self, obj: Category) -> dict | None:
        """
        Возвращает информацию о родительской категории.

        Формат:
            {
                "id": ...,
                "name": ...,
                "slug": ...
            }
        """
        if obj.parent:
            return {
                "id": obj.parent.id,
                "name": obj.parent.name,
                "slug": obj.parent.slug,
            }
        return None

    def get_children(self, obj: Category) -> list[dict[str, Any]]:
        """
        Возвращает одноуровневый список дочерних категорий.

        Формат:
            [
                {"id": ..., "name": ..., "slug": ...},
                ...
            ]
        """
        return [
            {
                "id": child.id,
                "name": child.name,
                "slug": child.slug,
            }
            for child in obj.children.all()
        ]
