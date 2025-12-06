from django.db.models import Q, Avg
from django_filters.views import FilterView
from django.views.generic import DetailView

from .models import Product, Category
from .filter import ProductFilter
from orders.models import OrderItem


class ProductListView(FilterView):
    """
    Каталог товаров: фильтры, поиск, сортировка, пагинация.
    """
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    filterset_class = ProductFilter
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Product.objects
            .filter(is_active=True)
            .select_related("category")
        )

        # Поиск
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )

        # Django Filter
        queryset = self.filterset_class(
            self.request.GET,
            queryset=queryset
        ).qs

        # Сортировка
        sort = self.request.GET.get("sort")
        allowed = {"price", "-price", "created_at", "-created_at"}

        queryset = queryset.order_by(sort) if sort in allowed else queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Категории
        context["categories"] = (
            Category.objects
            .filter(parent__isnull=True)
            .exclude(slug="default")
        )

        # Keywords (SEO)
        keywords_set = set()
        tags_qs = (
            Product.objects
            .exclude(tags__exact="")
            .values_list("tags", flat=True)
            .distinct()
        )

        for tag_string in tags_qs:
            for kw in tag_string.replace(";", ",").split(","):
                kw = kw.strip().lower()
                if kw:
                    keywords_set.add(kw)

        context["keywords_list"] = sorted(keywords_set)

        # Сохранение GET параметров для пагинации
        params = self.request.GET.copy()
        params.pop("page", None)
        context["current_params"] = params.urlencode()

        return context


class ProductDetailView(DetailView):
    """
    Детальная страница товара: характеристики, отзывы, рейтинг.
    """
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def user_can_review(self, product, user):
        """Проверка: купил ли пользователь продукт."""
        if not user.is_authenticated:
            return False

        return OrderItem.objects.filter(
            order__user=user,
            order__status="delivered",
            product=product
        ).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Характеристики
        context["specifications"] = product.specifications.all()

        # Отзывы (исправление review_set → related_name="reviews")
        context["reviews"] = (
            product.reviews
            .select_related("user")
            .order_by("-created_at")
        )

        # Средний рейтинг
        context["avg_rating"] = (
            product.reviews.aggregate(avg=Avg("rating"))["avg"] or 0
        )

        # Возможность оставить отзыв
        context["can_review"] = self.user_can_review(product, self.request.user)

        return context
