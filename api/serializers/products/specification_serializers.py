from __future__ import annotations

from rest_framework import serializers

from products.models import ProductSpecification


class ProductSpecificationSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели ProductSpecification.

    Используется как вложенный сериализатор в ProductSerializer.
    """

    class Meta:
        model = ProductSpecification
        fields = ["id", "name", "value"]
        read_only_fields = ["id"]
