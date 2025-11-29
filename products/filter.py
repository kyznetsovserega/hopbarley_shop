import django_filters
from django.db.models import Q

from.models import Product, Category



class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method="search",
        label="",
    )

    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
    )

    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
    )

    category = django_filters.CharFilter(
        method="filter_category",
        label="Category"
    )

    keywords = django_filters.CharFilter(
        method="filter_keywords",
        label=""
    )

    class Meta:
        model = Product
        fields = []

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )

    def filter_keywords(self, queryset, name, value):
        keywords = [k.strip().lower() for k in value.split(",") if k.strip()]
        for kw in keywords:
            queryset = queryset.filter(tags__icontains=kw)
        return queryset

    def filter_category(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(category__slug=value)
