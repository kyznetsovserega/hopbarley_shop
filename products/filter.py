"""
Фильтры каталога: поиск, цена, категория, ключевые слова.
"""

import django_filters
from django.db.models import Q

from .models import Product


class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="search", label="")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(method="filter_category", label="")
    keywords = django_filters.CharFilter(method="filter_keywords", label="")

    class Meta:
        model = Product
        fields = []

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )

    def filter_keywords(self, queryset, name, value):
        words = [w.strip().lower() for w in value.split(",") if w.strip()]
        for w in words:
            queryset = queryset.filter(tags__icontains=w)
        return queryset

    def filter_category(self, queryset, name, value):
        return queryset.filter(category__slug=value) if value else queryset
