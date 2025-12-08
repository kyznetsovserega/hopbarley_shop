"""
Админ-панель для категорий и товаров.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "parent")
    list_filter = ("parent",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "price",
        "old_price",
        "is_active",
        "stock",
        "preview",
        "created_at",
        "category",
    )
    list_filter = ("is_active", "category")
    search_fields = ("name", "description", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "preview_image")

    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "slug", "price", "old_price", "is_active", "stock", "category")
        }),
        ("Описание", {
            "fields": ("short_description", "description")
        }),
        ("Изображение", {
            "fields": ("image", "preview_image")
        }),
        ("Служебные поля", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;" />',
                obj.image.url
            )
        return "-"

    preview.short_description = "Image"

    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:200px;" />',
                obj.image.url
            )
        return "Нет изображений"

    preview_image.short_description = "Preview"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")
