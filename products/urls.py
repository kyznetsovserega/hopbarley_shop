from django.urls import path

from products.views import ProductListView, ProductDetailView

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(),name = "product_list"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]