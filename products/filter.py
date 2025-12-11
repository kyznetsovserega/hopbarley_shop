from __future__ import annotations

import django_filters
from django.db.models import Q, QuerySet

from .models import Product


class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="search", label="")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(method="filter_category", label="")
    keywords = django_filters.CharFilter(method="filter_keywords", label="")

    class Meta:
        model = Product
        fields: list[str] = []

    # ---------------------------------------------------------------
    # SEARCH (name + description)
    # ---------------------------------------------------------------
    def search(
        self, queryset: QuerySet[Product], name: str, value: str
    ) -> QuerySet[Product]:
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    # ---------------------------------------------------------------
    # KEYWORDS FILTER
    # ---------------------------------------------------------------
    def filter_keywords(
        self, queryset: QuerySet[Product], name: str, value: str
    ) -> QuerySet[Product]:
        if not value:
            return queryset

        words = [w.strip().lower() for w in value.split(",") if w.strip()]
        for w in words:
            queryset = queryset.filter(tags__icontains=w)
        return queryset

    # ---------------------------------------------------------------
    # CATEGORY FILTER
    # ---------------------------------------------------------------
    def filter_category(
        self, queryset: QuerySet[Product], name: str, value: str
    ) -> QuerySet[Product]:
        if not value:
            return queryset
        return queryset.filter(category__slug=value)
