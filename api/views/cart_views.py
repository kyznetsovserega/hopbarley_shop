from rest_framework import viewsets, permissions

from cart.models import CartItem
from api.serializers.cart_serializers import CartItemSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CartItem.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
