from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# Swagger / OpenAPI
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from users.views import account_view


urlpatterns = [
    path('admin/', admin.site.urls),

    # Short aliases (redirects)
    path('login/', lambda req: redirect('users:login')),
    path('register/', lambda req: redirect('users:register')),
    path('logout/', lambda req: redirect('users:logout')),
    path('forgot/', lambda req: redirect('users:forgot_password')),

    # Products
    path('', include(('products.urls', 'products'), namespace='products')),

    # Cart
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),

    # Orders
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),

    # Users
    path('users/', include(('users.urls', 'users'), namespace='users')),

    # Account
    path('account/', account_view, name='account'),

    # Reviews
    path('reviews/', include(('reviews.urls', 'reviews'), namespace='reviews')),

    # -------------------------
    # Swagger / OpenAPI Docs
    # -------------------------
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # API endpoints
    path('api/', include('api.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
