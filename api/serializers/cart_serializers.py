from rest_framework import  serializers
from cart.models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id',
            'user',
            'product',
            'quantity',
            'product_title',
            'product_price',
        ]
        read_only_fields = ['user']
