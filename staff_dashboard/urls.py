from django.urls import path

from . import views

app_name = "staff_dashboard"

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("products/", views.products, name="products"),
    path("products/add/", views.product_form, name="product_add"),
    path("products/<int:pk>/edit/", views.product_form, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
]
