from django.urls import path

from .views import checkout_view
from .views import fake_payment_success
from .views import fake_payment_view
from .views import order_success_view

app_name = "orders"

urlpatterns = [
    path("checkout/", checkout_view, name="checkout"),
    path("success/<int:order_id>/", order_success_view, name="success"),
    path("fake-payment/<int:order_id>/", fake_payment_view, name="fake_payment"),
    path(
        "fake-payment-success/<int:order_id>/",
        fake_payment_success,
        name="fake_payment_success",
    ),
]
