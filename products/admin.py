from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from .models import Category
from .models import Product
from .models import ProductSpecification

# ============================================================
# INLINE: Характеристики товара
# ============================================================


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    min_num = 0
    verbose_name = "Характеристика"
    verbose_name_plural = "Характеристики"
    fields = ("name", "value")
    ordering = ("id",)


# ============================================================
# CATEGORY ADMIN
# ============================================================


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "parent")
    list_filter = ("parent",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Category]:
        qs: QuerySet[Category] = super().get_queryset(request)
        return qs.select_related("parent")


# ============================================================
# ACTIONS
# ============================================================


@admin.action(description="Сделать активными")
def activate_products(
    modeladmin: admin.ModelAdmin[Any],
    request: HttpRequest,
    queryset: QuerySet[Product],
) -> None:
    queryset.update(is_active=True)


@admin.action(description="Сделать неактивными")
def deactivate_products(
    modeladmin: admin.ModelAdmin[Any],
    request: HttpRequest,
    queryset: QuerySet[Product],
) -> None:
    queryset.update(is_active=False)


# ============================================================
# PRODUCT ADMIN
# ============================================================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "category",
        "price",
        "old_price",
        "is_active",
        "stock",
        "preview",
        "created_at",
    )

    list_filter = ("is_active", "category", "created_at")

    search_fields = ("name", "description", "short_description", "tags")

    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "preview_image")

    inlines = [ProductSpecificationInline]

    actions = [activate_products, deactivate_products]

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "name",
                    "slug",
                    "category",
                    "price",
                    "old_price",
                    "is_active",
                    "stock",
                )
            },
        ),
        ("Описание", {"fields": ("short_description", "description")}),
        ("Изображение", {"fields": ("image", "preview_image")}),
        ("SEO / Теги", {"fields": ("tags",)}),
        ("Служебные поля", {"fields": ("created_at", "updated_at")}),
    )

    # ============================================================
    # PREVIEW METHODS
    # ============================================================

    @admin.display(description="Preview")
    def preview(self, obj: Product) -> str:
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;'
                'object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        return "-"

    @admin.display(description="Изображение")
    def preview_image(self, obj: Product) -> str:
        if obj.image:
            return format_html(
                '<img src="{}" style="width:200px;border-radius:6px;" />',
                obj.image.url,
            )
        return "(Нет изображения)"

    # ============================================================
    # OPTIMIZED QUERYSET
    # ============================================================

    def get_queryset(self, request: HttpRequest) -> QuerySet[Product]:
        qs: QuerySet[Product] = super().get_queryset(request)
        return qs.select_related("category").prefetch_related("specifications")
