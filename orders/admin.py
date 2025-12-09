from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, F

from .models import Order, OrderItem


# =====================================================================
# INLINE для OrderItem
# =====================================================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    raw_id_fields = ("product",)
    readonly_fields = ("product", "quantity", "price", "total")

    def total(self, obj):
        return f"{obj.quantity * obj.price:.2f}"
    total.short_description = "Сумма"


# =====================================================================
# Actions
# =====================================================================
@admin.action(description="Отметить как оплаченные")
def mark_as_paid(modeladmin, request, queryset):
    queryset.update(status=Order.STATUS_PAID)


@admin.action(description="Отменить заказ")
def cancel_orders(modeladmin, request, queryset):
    queryset.update(status=Order.STATUS_CANCELLED)


@admin.action(description="Отметить как отправленные")
def mark_as_shipped(modeladmin, request, queryset):
    queryset.update(status=Order.STATUS_SHIPPED)


# =====================================================================
# Фильтр по сумме заказа
# =====================================================================
class TotalPriceFilter(admin.SimpleListFilter):
    title = "Сумма заказа"
    parameter_name = "total_price_range"

    def lookups(self, request, model_admin):
        return [
            ("0_50", "до 50"),
            ("50_100", "50 – 100"),
            ("100_200", "100 – 200"),
            ("200_plus", "более 200"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        if value == "0_50":
            return queryset.filter(total_price__lt=50)
        if value == "50_100":
            return queryset.filter(total_price__gte=50, total_price__lt=100)
        if value == "100_200":
            return queryset.filter(total_price__gte=100, total_price__lt=200)
        if value == "200_plus":
            return queryset.filter(total_price__gte=200)

        return queryset


# =====================================================================
# ORDER ADMIN
# =====================================================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "buyer",
        "contact_phone",
        "status_colored",
        "payment_method",
        "total_price",
        "items_count",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        TotalPriceFilter,
        "created_at",
    )

    search_fields = (
        "id",
        "full_name",
        "email",
        "phone",
        "user__username",
    )

    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    inlines = [OrderItemInline]

    readonly_fields = (
        "user",
        "session_key",
        "status",
        "payment_method",
        "total_price",
        "items_count",
        "created_at",
        "updated_at",
    )

    actions = (mark_as_paid, mark_as_shipped, cancel_orders)

    # ----------------------------------------------------------------------
    # Оптимизация запросов
    # ----------------------------------------------------------------------
    def get_queryset(self, request):
        qs = (
            super().get_queryset(request)
            .prefetch_related("items")
            .select_related("user")
        )
        return qs

    # ----------------------------------------------------------------------
    # АГРЕГИРОВАННАЯ АНАЛИТИКА
    # ----------------------------------------------------------------------
    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)

        # АГРЕГАТЫ
        stats = qs.aggregate(
            total_orders=Count("id"),
            total_revenue=Sum("total_price"),
        )

        # Средний чек считаем в Python
        total_orders = stats.get("total_orders") or 0
        total_revenue = stats.get("total_revenue") or 0

        avg_check = total_revenue / total_orders if total_orders > 0 else 0
        stats["avg_check"] = avg_check

        # Количество заказов в статусе PENDING
        pending = qs.filter(status=Order.STATUS_PENDING).count()

        # Топ 5 товаров
        top_products = (
            OrderItem.objects
            .values(name=F("product__name"))
            .annotate(total_qty=Sum("quantity"))
            .order_by("-total_qty")[:5]
        )

        extra_context = extra_context or {}
        extra_context["stats"] = stats
        extra_context["pending"] = pending
        extra_context["top_products"] = top_products

        return super().changelist_view(request, extra_context=extra_context)

    # ----------------------------------------------------------------------
    # UI helpers
    # ----------------------------------------------------------------------
    def buyer(self, obj):
        return obj.full_name or "—"
    buyer.short_description = "Клиент"

    def contact_phone(self, obj):
        return obj.phone or "—"
    contact_phone.short_description = "Телефон"

    def status_colored(self, obj):
        colors = {
            Order.STATUS_PENDING: "gray",
            Order.STATUS_PENDING_PAYMENT: "orange",
            Order.STATUS_PAID: "green",
            Order.STATUS_SHIPPED: "blue",
            Order.STATUS_DELIVERED: "purple",
            Order.STATUS_CANCELLED: "red",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_colored.short_description = "Статус"


# =====================================================================
# ORDER ITEM ADMIN
# =====================================================================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
        "total",
    )
    raw_id_fields = ("product", "order")

    search_fields = (
        "product__name",
        "order__id",
    )

    def total(self, obj):
        return f"{obj.quantity * obj.price:.2f}"
