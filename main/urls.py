from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

# Swagger / OpenAPI
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# GraphQL
from graphene_django.views import GraphQLView

# Local views
from users.views import account_view

urlpatterns = [
    # -------------------------------------------------
    # Admin
    path("admin/", admin.site.urls),
    # -------------------------------------------------
    # Short aliases (redirects)
    # -------------------------------------------------
    path("login/", lambda request: redirect("users:login")),
    path("register/", lambda request: redirect("users:register")),
    path("logout/", lambda request: redirect("users:logout")),
    path("forgot/", lambda request: redirect("users:forgot_password")),
    # -------------------------------------------------
    # Web (Django views)
    # -------------------------------------------------
    path("", include(("products.urls", "products"), namespace="products")),
    path("cart/", include(("cart.urls", "cart"), namespace="cart")),
    path("orders/", include(("orders.urls", "orders"), namespace="orders")),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("reviews/", include(("reviews.urls", "reviews"), namespace="reviews")),
    path("account/", account_view, name="account"),
    # -------------------------------------------------
    # REST API
    # -------------------------------------------------
    path("api/", include("api.urls")),
    # -------------------------------------------------
    # Swagger / OpenAPI
    # -------------------------------------------------
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
    # -------------------------------------------------
    # GraphQL
    # -------------------------------------------------
    path(
        "graphql/",
        csrf_exempt(GraphQLView.as_view(graphiql=True)),
        name="graphql",
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
