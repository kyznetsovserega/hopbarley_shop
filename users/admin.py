from __future__ import annotations

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Sum, Max, QuerySet

from .models import UserProfile


User = get_user_model()


# =========================================================
# INLINE: USER PROFILE
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

    def lookups(self, request, model_admin):
        return [
            ("yes", "Has orders"),
            ("no", "No orders"),
        ]

    def queryset(self, request, qs: QuerySet):
        if self.value() == "yes":
            return qs.filter(order_count__gt=0)
        if self.value() == "no":
            return qs.filter(order_count=0)
        return qs


class BigSpendersFilter(admin.SimpleListFilter):
    """Фильтр пользователей с суммой заказов > 200$."""
    title = "Top Customers"
    parameter_name = "top_customers"

    def lookups(self, request, model_admin):
        return [
            ("200", "> 200$ spent"),
            ("500", "> 500$ spent"),
        ]

    def queryset(self, request, qs: QuerySet):
        if self.value() == "200":
            return qs.filter(total_spent__gt=200)
        if self.value() == "500":
            return qs.filter(total_spent__gt=500)
        return qs


class CityFilter(admin.SimpleListFilter):
    """Фильтр по городу."""
    title = "City"
    parameter_name = "city"

    def lookups(self, request, model_admin):
        cities = (
            UserProfile.objects.exclude(city="")
            .order_by("city")
            .values_list("city", flat=True)
            .distinct()
        )
        return [(c, c) for c in cities]

    def queryset(self, request, qs: QuerySet):
        if self.value():
            return qs.filter(profile__city=self.value())
        return qs


# =========================================================
# CUSTOM USER ADMIN
# =========================================================

class CustomUserAdmin(UserAdmin):
    """
    — Inline профиль
    — Аналитика заказов
    — Поиск, фильтры
    — Экшены
    """

    inlines = [UserProfileInline]

    # ---- АННОТАЦИИ ORM ----
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs
            .select_related("profile")
            .annotate(
                order_count=Count("orders", distinct=True),
                total_spent=Sum("orders__total_price"),
                last_order=Max("orders__created_at"),
            )
        )

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

    def get_phone(self, obj):
        return obj.profile.phone or "—"
    get_phone.short_description = "Phone"

    def get_city(self, obj):
        return obj.profile.city or "—"
    get_city.short_description = "City"

    def get_orders_count(self, obj):
        return obj.order_count or 0
    get_orders_count.short_description = "Orders"

    def get_total_spent(self, obj):
        total = obj.total_spent or 0
        return f"${total:.2f}"
    get_total_spent.short_description = "Total Spent"

    def get_last_order(self, obj):
        if obj.last_order:
            return obj.last_order.strftime("%Y-%m-%d")
        return "—"
    get_last_order.short_description = "Last Order"

    # =========================================================
    # ACTIONS
    # =========================================================

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, qs):
        qs.update(is_active=False)

    @admin.action(description="Activate selected users")
    def activate_users(self, request, qs):
        qs.update(is_active=True)

    @admin.action(description="Reset profiles (clear city & address)")
    def clear_profiles(self, request, qs):
        profiles = UserProfile.objects.filter(user__in=qs)
        profiles.update(city="", address="")

    actions = [
        "deactivate_users",
        "activate_users",
        "clear_profiles",
    ]


# Перерегистрируем User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
