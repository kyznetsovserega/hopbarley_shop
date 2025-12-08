from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Отображение товарных позиций внутри заказа.
    Используется только для просмотра — добавлять/удалять вручную нельзя.
    """
    model = OrderItem
    extra = 0
    raw_id_fields = ("product",)
    readonly_fields = ("product", "quantity", "price", "total")
    can_delete = False

    def total(self, obj):
        return obj.quantity * obj.price

    total.short_description = "Сумма"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Админка заказов.
    Позволяет удобно просматривать данные заказа,
    фильтровать по статусу и дате, искать по контактам.
    """

    list_display = (
        "id",
        "full_name",
        "email",
        "phone",
        "status",
        "total_price",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "id",
        "full_name",
        "email",
        "phone",
        "user__username",
    )
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]

    readonly_fields = (
        "user",
        "session_key",
        "total_price",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Админка товарных позиций заказов.
    """
    list_display = ("id", "order", "product", "quantity", "price", "total")
    raw_id_fields = ("product", "order")
    search_fields = ("product__name", "order__id")

    def total(self, obj):
        return obj.quantity * obj.price

    total.short_description = "Сумма"
