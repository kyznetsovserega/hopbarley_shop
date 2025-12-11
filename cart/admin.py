from __future__ import annotations

from django.contrib import admin
from django.db.models import F, QuerySet
from django.http import HttpRequest

from cart.models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Админка корзины.

    - отображение суммы позиции (total_price)
    - оптимизированный queryset (select_related + аннотация)
    - фильтрация по пользователю / продукту / типу корзины
    - быстрый поиск по товарам, пользователям и session_key
    - actions для чистки корзин
    """

    list_display = (
        "id",
        "product_name",
        "quantity",
        "total_price_display",
        "owner",
        "cart_type",
        "session_key",
    )

    list_filter = (
        "product",
        "user",
        "quantity",
        ("session_key", admin.EmptyFieldListFilter),
    )

    search_fields = (
        "product__name",
        "user__username",
        "user__email",
        "session_key",
    )

    ordering = ("id",)

    # ------------------------------------------------------------------
    # ORM оптимизация
    # ------------------------------------------------------------------
    def get_queryset(self, request: HttpRequest) -> QuerySet[CartItem]:
        qs: QuerySet[CartItem] = super().get_queryset(request)
        return qs.select_related("product", "user").annotate(
            annotated_total=F("quantity") * F("product__price")
        )

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------
    @admin.display(description="Product")
    def product_name(self, obj: CartItem) -> str:
        return f"{obj.product.name} ({obj.product.price}$)"

    @admin.display(description="Total", ordering="annotated_total")
    def total_price_display(self, obj: CartItem) -> str:
        return f"{obj.annotated_total:.2f}"

    @admin.display(description="Owner")
    def owner(self, obj: CartItem) -> str:
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "—"

    @admin.display(description="Type")
    def cart_type(self, obj: CartItem) -> str:
        return "User" if obj.user else "Guest"

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    actions = ["delete_guest_carts", "delete_inactive_products", "clear_selected"]

    @admin.action(description="Удалить все гостевые корзины")
    def delete_guest_carts(
        self,
        request: HttpRequest,
        queryset: QuerySet[CartItem],
    ) -> None:
        count = queryset.filter(user__isnull=True, session_key__isnull=False).count()
        queryset.filter(user__isnull=True, session_key__isnull=False).delete()
        self.message_user(request, f"Удалено гостевых позиций: {count}")

    @admin.action(description="Удалить позиции с неактивными товарами")
    def delete_inactive_products(
        self,
        request: HttpRequest,
        queryset: QuerySet[CartItem],
    ) -> None:
        count = queryset.filter(product__is_active=False).count()
        queryset.filter(product__is_active=False).delete()
        self.message_user(request, f"Удалено: {count} позиций с неактивными товарами")

    @admin.action(description="Удалить выбранные позиции")
    def clear_selected(
        self,
        request: HttpRequest,
        queryset: QuerySet[CartItem],
    ) -> None:
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Удалено позиций: {count}")
