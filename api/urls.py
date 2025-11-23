from rest_framework.routers import DefaultRouter
from api.views.product_views import ProductViewSet
from api.views.category_views import CategoryViewSet
from api.views.cart_views import CartViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'cart', CartViewSet, basename='cartitem')

urlpatterns = router.urls