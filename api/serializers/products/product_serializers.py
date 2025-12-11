from __future__ import annotations

from typing import Any, Dict, List

from rest_framework import serializers

from products.models import Product

from .category_serializers import CategorySerializer
from .specification_serializers import ProductSpecificationSerializer


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Product.

    Возвращает:
        - вложенную категорию (CategorySerializer)
        - вложенные характеристики товара (ProductSpecificationSerializer)
        - вычисляемые поля скидки (is_discounted, discount_percent)
    """

    category: CategorySerializer = CategorySerializer(read_only=True)
    specifications: List[Dict[str, Any]] = ProductSpecificationSerializer(
        many=True, read_only=True
    )

    is_discounted: serializers.BooleanField = serializers.BooleanField(read_only=True)
    discount_percent: serializers.IntegerField = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "description",
            "unit",
            "price",
            "old_price",
            "stock",
            "image",
            "is_active",
            "tags",
            "is_discounted",
            "discount_percent",
            "specifications",
            "created_at",
            "updated_at",
            "category",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
