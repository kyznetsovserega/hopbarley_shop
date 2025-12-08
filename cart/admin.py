from django.contrib import admin
from cart.models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Админ-панель элементов корзины.

    Позволяет просматривать корзины пользователей и гостей.
    """

    list_display = ("id", "product", "quantity", "user", "session_key")
    list_filter = ("user",)
    search_fields = ("product__name", "session_key")
    ordering = ("id",)

    readonly_fields = ()
