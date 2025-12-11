from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from django.db.models import Avg, Count, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.views.generic import DetailView
from django_filters.views import FilterView

from orders.models import OrderItem
from reviews.forms import ReviewForm
from reviews.models import Review

from .filter import ProductFilter
from .models import Category, Product

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as UserType
else:
    UserType = Any


# -------------------------------------------------------------------------
#  PRODUCT LIST VIEW
# -------------------------------------------------------------------------


class ProductListView(FilterView):
    """
    Каталог товаров: фильтры, поиск, сортировка, пагинация.
    """

    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    filterset_class = ProductFilter
    paginate_by = 12

    def get_queryset(self) -> QuerySet[Product]:
        queryset: QuerySet[Product] = Product.objects.filter(
            is_active=True
        ).select_related("category")

        # Поиск
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

        # django-filter
        queryset = self.filterset_class(
            self.request.GET,
            queryset=queryset,
        ).qs

        # Сортировка
        sort = self.request.GET.get("sort")
        allowed = {"price", "-price", "created_at", "-created_at"}

        if sort in allowed:
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context: Dict[str, Any] = super().get_context_data(**kwargs)

        # Список корневых категорий
        context["categories"] = Category.objects.filter(parent__isnull=True).exclude(
            slug="default"
        )

        # Keywords (SEO)
        keywords_set: set[str] = set()
        tags_qs = (
            Product.objects.exclude(tags__exact="")
            .values_list("tags", flat=True)
            .distinct()
        )

        for tag_string in tags_qs:
            for kw in tag_string.replace(";", ",").split(","):
                kw = kw.strip().lower()
                if kw:
                    keywords_set.add(kw)

        context["keywords_list"] = sorted(keywords_set)

        # Параметры запроса без page — для пагинации
        params = self.request.GET.copy()
        params.pop("page", None)
        context["current_params"] = params.urlencode()

        return context


# -------------------------------------------------------------------------
#  PRODUCT DETAIL VIEW
# -------------------------------------------------------------------------


class ProductDetailView(DetailView):
    """
    Детальная страница товара: характеристики, отзывы, рейтинг.
    """

    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    invalid_form: ReviewForm | None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.invalid_form = None

    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        # Если extra_context передан — забираем invalid_form
        if hasattr(self, "extra_context") and self.extra_context:
            self.invalid_form = self.extra_context.get("invalid_form")
        return super().dispatch(request, *args, **kwargs)

    # --- Проверки (купил товар + писал раньше отзыв) ---

    def user_has_bought(self, product: Product, user: UserType) -> bool:
        """
        Проверка: купил ли пользователь товар.
        Статусы: paid или delivered.
        """
        if not getattr(user, "is_authenticated", False):
            return False

        return OrderItem.objects.filter(
            order__user=user,
            order__status__in=["paid", "delivered"],
            product=product,
        ).exists()

    def user_already_reviewed(self, product: Product, user: UserType) -> bool:
        """Проверка: писал ли пользователь отзыв ранее."""
        if not getattr(user, "is_authenticated", False):
            return False

        return Review.objects.filter(
            user=user,
            product=product,
        ).exists()

    # --- Контекст страницы ---

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context: Dict[str, Any] = super().get_context_data(**kwargs)

        product: Product = self.object
        user: UserType = self.request.user

        # Характеристики товара
        context["specifications"] = product.specifications.all()

        # Все отзывы
        reviews_qs = product.reviews.select_related("user").order_by("-created_at")
        context["reviews"] = reviews_qs

        # Агрегация по отзывам
        agg = reviews_qs.aggregate(avg_rating=Avg("rating"), count=Count("id"))
        context["average_rating"] = agg["avg_rating"] or 0
        context["reviews_count"] = agg["count"] or 0

        # Проверки
        has_bought = self.user_has_bought(product, user)
        already_reviewed = self.user_already_reviewed(product, user)

        context["can_review"] = has_bought and not already_reviewed
        context["already_reviewed"] = already_reviewed

        # Форма: пустая или с ошибками
        context["review_form"] = (
            self.invalid_form if self.invalid_form else ReviewForm()
        )

        return context
