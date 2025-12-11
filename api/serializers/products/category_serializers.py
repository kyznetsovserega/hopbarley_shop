from __future__ import annotations

from typing import Any, Dict, List, Optional

from django.db.models import QuerySet
from rest_framework import serializers

from products.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Category.

    Возвращает сведения о родительской категории (parent)
    и список дочерних категорий первого уровня (children).
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

    def get_parent(self, obj: Category) -> Optional[Dict[str, Any]]:
        """
        Возвращает краткую информацию о родительской категории:

        {
            "id": ...,
            "name": ...,
            "slug": ...
        }
        """
        parent = obj.parent
        if parent is None:
            return None

        return {
            "id": parent.id,
            "name": parent.name,
            "slug": parent.slug,
        }

    def get_children(self, obj: Category) -> List[Dict[str, Any]]:
        """
        Возвращает одноуровневый список дочерних категорий:

        [
            {"id": ..., "name": ..., "slug": ...},
            ...
        ]
        """
        children: QuerySet[Category] = obj.children.all()

        return [
            {
                "id": child.id,
                "name": child.name,
                "slug": child.slug,
            }
            for child in children
        ]
