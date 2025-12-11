from django.urls import path

from products.views import ProductDetailView
from products.views import ProductListView

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]
