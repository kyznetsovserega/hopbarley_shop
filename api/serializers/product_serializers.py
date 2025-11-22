from rest_framework import serializers
from products.models import Product
from .category_serializers import CategorySerializer

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        field = [
            'id',
            'name',
            'slug',
            'description',
            'price',
            'stock',
            'image',
            'is_active',
            'create_at',
            'category',
        ]