from rest_framework import viewsets, filters
from products.models import Product
from api.serializers.product_serializers import ProductSerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name','description']
    ordering_fields = ['price', 'created_at']
    