from rest_framework import viewsets, filters
from cart.models import CartItem
from api.serializers.cart_serializers import CartItemSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer