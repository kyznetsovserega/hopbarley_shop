from rest_framework.routers import DefaultRouter
from api.views.product_views import ProductViewSet
from api.views.category_views import CategoryViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = router.urls