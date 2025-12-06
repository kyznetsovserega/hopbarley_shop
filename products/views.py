from django_filters.views import FilterView
from django.views.generic import DetailView

from django.db.models import Avg, Count

from reviews.forms import ReviewForm
from .models import Product, Category
from .filter import ProductFilter


class ProductListView(FilterView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    filterset_class = ProductFilter
    paginate_by = 2

    def get_queryset(self):
        queryset = (
            Product.objects
            .filter(is_active=True)
            .select_related("category")
        )

        queryset = self.filterset_class(
            self.request.GET,
            queryset=queryset
        ).qs

        sort = self.request.GET.get("sort")
        allowed = {"price", "-price","created_at", "-created_at"}

        if sort in allowed:
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = (
            Category.objects
            .filter(parent__isnull=True)
            .exclude(slug="default")
        )

        all_tags = (
            Product.objects
            .exclude(tags__exact="")
            .values_list("tags", flat=True)
            .distinct()
        )

        keywords_set = set()

        for tag_string in all_tags:
            for kw in tag_string.replace(";", ",").split(","):
                kw = kw.strip().lower()
                if kw:
                    keywords_set.add(kw)

        context["keywords_list"] = sorted(keywords_set)

        params = self.request.GET.copy()

        if "page" in params:
            params.pop("page")

        context["current_params"] = params.urlencode()

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Все отзывы по продукту
        reviews_qs = product.reviews.select_related("user").order_by("-created_at")
        context["reviews"] = reviews_qs

        # Агрегация: средний рейтинг и кол-во отзывов
        agg = reviews_qs.aggregate(
            avg_rating=Avg("rating"),
            count=Count("id"),
        )

        context["average_rating"] = agg["avg_rating"] or 0
        context["reviews_count"] = agg["count"] or 0

        # Пустая форма для создания отзыва
        context["review_form"] = ReviewForm()

        return context
