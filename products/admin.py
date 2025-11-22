from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','slug', 'parent')
    search_fields = ('name', 'slug')
    list_filter = ('parent',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','slug', 'price', 'is_active', 'stock', 'category')
    search_fields = ('is_active', 'category')
    list_filter = ('name','slug','description')