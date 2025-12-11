from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Tuple

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Max, QuerySet, Sum
from django.http import HttpRequest

from .models import UserProfile

# ---------------------------------------------------------
# Тип модели пользователя
# ---------------------------------------------------------
User = get_user_model()

if TYPE_CHECKING:

    from django.contrib.auth.models import AbstractUser as UserType
else:
    UserType = Any


# =========================================================
# INLINE
# =========================================================


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fk_name = "user"

    fields = (
        "phone",
        "city",
        "address",
        "date_of_birth",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    extra = 0


# =========================================================
# FILTERS
# =========================================================


class HasOrdersFilter(admin.SimpleListFilter):
    """Пользователи с заказами / без заказов."""

    title = "Has Orders"
    parameter_name = "has_orders"

    def lookups(
        self,
        request: HttpRequest,
        model_admin: admin.ModelAdmin[Any],
    ) -> List[Tuple[str, str]]:
        return [
            ("yes", "Has orders"),
            ("no", "No orders"),
        ]

    def queryset(
        self,
        request: HttpRequest,
        qs: QuerySet[UserType],
    ) -> QuerySet[UserType]:
        match self.value():
            case "yes":
                return qs.filter(order_count__gt=0)
            case "no":
                return qs.filter(order_count=0)
            case _:
                return qs


class BigSpendersFilter(admin.SimpleListFilter):
    """Фильтр пользователей с суммой заказов > 200$."""

    title = "Top Customers"
    parameter_name = "top_customers"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin[Any]) -> List[Tuple[str, str]]:
        return [
            ("200", "> 200$ spent"),
            ("500", "> 500$ spent"),
        ]

    def queryset(
        self,
        request: HttpRequest,
        qs: QuerySet[UserType],
    ) -> QuerySet[UserType]:
        match self.value():
            case "200":
                return qs.filter(total_spent__gt=200)
            case "500":
                return qs.filter(total_spent__gt=500)
            case _:
                return qs


class CityFilter(admin.SimpleListFilter):
    """Фильтр по городу."""

    title = "City"
    parameter_name = "city"

    def lookups(
        self,
        request: HttpRequest,
        model_admin: admin.ModelAdmin[Any],
    ) -> List[Tuple[str, str]]:
        cities = UserProfile.objects.exclude(city="").order_by("city").values_list("city", flat=True).distinct()
        return [(str(c), str(c)) for c in cities]

    def queryset(self, request: HttpRequest, qs: QuerySet[UserType]) -> QuerySet[UserType]:
        if city := self.value():
            return qs.filter(profile__city=city)
        return qs


# =========================================================
# CUSTOM USER ADMIN
# =========================================================


class CustomUserAdmin(UserAdmin):
    """
    Inline профиль + аналитика заказов.
    """

    inlines: List[type[admin.StackedInline]] = [UserProfileInline]

    # ---- АННОТИРОВАННЫЙ QUERYSET ----
    def get_queryset(self, request: HttpRequest) -> QuerySet[UserType]:
        qs: QuerySet[UserType] = super().get_queryset(request)
        annotated = qs.select_related("profile").annotate(
            order_count=Count("orders", distinct=True),
            total_spent=Sum("orders__total_price"),
            last_order=Max("orders__created_at"),
        )
        return annotated

    # ---- LIST DISPLAY ----
    list_display = UserAdmin.list_display + (
        "get_phone",
        "get_city",
        "get_orders_count",
        "get_total_spent",
        "get_last_order",
    )

    list_filter = UserAdmin.list_filter + (
        HasOrdersFilter,
        BigSpendersFilter,
        CityFilter,
    )

    search_fields = UserAdmin.search_fields + (
        "email",
        "profile__phone",
        "profile__city",
    )

    ordering = ("-date_joined",)

    # =========================================================
    # DISPLAY METHODS
    # =========================================================

    @admin.display(description="Phone")
    def get_phone(self, obj: UserType) -> str:
        profile = getattr(obj, "profile", None)
        return getattr(profile, "phone", "—") or "—"

    @admin.display(description="City")
    def get_city(self, obj: UserType) -> str:
        profile = getattr(obj, "profile", None)
        return getattr(profile, "city", "—") or "—"

    @admin.display(description="Orders")
    def get_orders_count(self, obj: UserType) -> int:
        val = getattr(obj, "order_count", 0)
        return int(val or 0)

    @admin.display(description="Total Spent")
    def get_total_spent(self, obj: UserType) -> str:
        total = getattr(obj, "total_spent", 0) or 0
        return f"${total:.2f}"

    @admin.display(description="Last Order")
    def get_last_order(self, obj: UserType) -> str:
        dt = getattr(obj, "last_order", None)
        return dt.strftime("%Y-%m-%d") if dt else "—"

    # =========================================================
    # ACTIONS
    # =========================================================

    @admin.action(description="Deactivate selected users")
    def deactivate_users(
        self,
        request: HttpRequest,
        qs: QuerySet[UserType],
    ) -> None:
        qs.update(is_active=False)

    @admin.action(description="Activate selected users")
    def activate_users(
        self,
        request: HttpRequest,
        qs: QuerySet[UserType],
    ) -> None:
        qs.update(is_active=True)

    @admin.action(description="Reset profiles (clear city & address)")
    def clear_profiles(
        self,
        request: HttpRequest,
        qs: QuerySet[UserType],
    ) -> None:
        profiles = UserProfile.objects.filter(user__in=qs)
        profiles.update(city="", address="")

    actions = [
        "deactivate_users",
        "activate_users",
        "clear_profiles",
    ]


# Регистрируем
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
