from __future__ import annotations

from typing import Optional, List

import graphene
from django.db.models import Q, QuerySet
from graphene import ResolveInfo

from products.models import Product, Category
from graphql_api.types.product_types import ProductType, CategoryType


# ================================
# Глобальные настройки для сортировки
# ================================

ALLOWED_SORT_FIELDS: List[str] = [
    "price",
    "-price",
    "created_at",
    "-created_at",
    "name",
    "-name",
]


class ProductQuery(graphene.ObjectType):
    """
    GraphQL запросы для каталога продукции:
    - всеТовары: список с фильтрами, поиском, нумерацией страниц, сортировкой
    - продукт: получить продукт по пуле
    - категории: список доступных категорий.
    """

    all_products = graphene.List(
        ProductType,
        search=graphene.String(required=False),
        category=graphene.String(required=False),
        order_by=graphene.String(required=False),
        price_min=graphene.Float(required=False),
        price_max=graphene.Float(required=False),
        in_stock=graphene.Boolean(required=False),
        discounted=graphene.Boolean(required=False),
        limit=graphene.Int(required=False),
        offset=graphene.Int(required=False),
        description="Returns filtered list of active products.",
    )

    product = graphene.Field(
        ProductType,
        slug=graphene.String(required=True),
        description="Returns a single product by slug.",
    )

    categories = graphene.List(
        CategoryType,
        description="Returns list of product categories.",
    )

    # ============================================================
    # RESOLVERS
    # ============================================================

    def resolve_all_products(
        self,
        info: ResolveInfo,
        search: Optional[str] = None,
        category: Optional[str] = None,
        order_by: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        in_stock: Optional[bool] = None,
        discounted: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> QuerySet[Product]:

        qs = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("specifications")
        )

        # SEARCH
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(short_description__icontains=search)
                | Q(description__icontains=search)
                | Q(tags__icontains=search)
            )

        # CATEGORY FILTER
        if category:
            qs = qs.filter(category__slug=category)

        # PRICE FILTERS
        if price_min is not None:
            qs = qs.filter(price__gte=price_min)

        if price_max is not None:
            qs = qs.filter(price__lte=price_max)

        # STOCK
        if in_stock is True:
            qs = qs.filter(stock__gt=0)

        # DISCOUNTED
        if discounted is True:
            qs = qs.filter(old_price__gt=models.F("price"))

        # SORTING
        if order_by:
            if order_by in ALLOWED_SORT_FIELDS:
                qs = qs.order_by(order_by)
            else:
                raise ValueError(f"Invalid sorting field: {order_by}")

        # PAGINATION
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]

        return qs

    # ---------------------------------------------------------
    def resolve_product(self, info: ResolveInfo, slug: str) -> Optional[Product]:
        try:
            return (
                Product.objects.select_related("category")
                .prefetch_related("specifications")
                .get(slug=slug)
            )
        except Product.DoesNotExist:
            raise ValueError(f"Product with slug '{slug}' not found.")

    # ---------------------------------------------------------
    def resolve_categories(
        self,
        info: ResolveInfo,
    ) -> QuerySet[Category]:
        return Category.objects.all()
