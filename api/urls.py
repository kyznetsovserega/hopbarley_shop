from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views.cart_views import CartItemViewSet
from api.views.order_views import OrderViewSet
from api.views.products.category_views import CategoryViewSet
from api.views.products.product_views import ProductViewSet
from api.views.review_views import ReviewViewSet
from api.views.user_views import MeView, RegisterView, UpdateProfileView

# ---------------------------------------------------------
# DRF Router — добавляем ТОЛЬКО ViewSets
# ---------------------------------------------------------
router = DefaultRouter()

# Каталог
router.register(r"products", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet, basename="category")

# Корзина
router.register(r"cart", CartItemViewSet, basename="cartitem")

# Отзывы
router.register(r"reviews", ReviewViewSet, basename="review")

# Заказы
router.register(r"orders", OrderViewSet, basename="order")

# ---------------------------------------------------------
# URL patterns для Users API + JWT
# ---------------------------------------------------------
urlpatterns = [
    # Регистрация
    path("users/register/", RegisterView.as_view(), name="user-register"),
    # JWT логин / refresh
    path("users/login/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("users/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # Профиль
    path("users/me/", MeView.as_view(), name="user-me"),
    path("users/me/update/", UpdateProfileView.as_view(), name="user-update-profile"),
]

# Добавляем маршруты router
urlpatterns += router.urls
