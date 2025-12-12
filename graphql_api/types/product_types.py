from __future__ import annotations

import graphene
from graphene_django import DjangoObjectType

from products.models import (
    Product,
    Category,
    ProductSpecification,
)


class CategoryType(DjangoObjectType):
    """
    GraphQL тип для категорий товаров.
    Поддерживает вложенные категории через поле `children`.
    """

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "children",
        )
        description = "Product category with support for nested hierarchy."


class ProductSpecificationType(DjangoObjectType):
    """
    Характеристика товара вида «Имя — Значение».
    """

    class Meta:
        model = ProductSpecification
        fields = (
            "id",
            "name",
            "value",
        )
        description = "Product specification key-value pair."


class ProductType(DjangoObjectType):
    """
    Базовый GraphQL тип товара.
    Содержит вычисляемые поля:
    - discountPercent (camelCase): процент скидки
    """

    discount_percent = graphene.Int(
        description="Discount percentage calculated from price and old_price."
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "short_description",
            "description",
            "unit",
            "price",
            "old_price",
            "is_discounted",
            "discount_percent",
            "category",
            "image",
            "is_active",
            "stock",
            "tags",
            "specifications",
        )
        description = "Product entity with pricing, category and specifications."

    # -------------------------------
    # Custom Resolvers
    # -------------------------------

    def resolve_discount_percent(self, info) -> int:
        """
        Возвращает процент скидки.
        Безопасно обрабатывает случай отсутствия old_price.
        """
        if not self.old_price or self.old_price <= 0:
            return 0
        return int(100 - (float(self.price) / float(self.old_price) * 100))
