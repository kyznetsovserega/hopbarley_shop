import pytest
from django.urls import reverse
from django.test import Client
from cart.models import CartItem
from orders.models import Order


# ============================================================================
# 1. SUCCESS CHECKOUT
# ============================================================================

@pytest.mark.django_db
def test_checkout_success(product_fixture, web_session_key):
    client = Client()

    # Правильный session_key через cookie
    client.cookies["sessionid"] = web_session_key

    CartItem.objects.create(
        session_key=web_session_key,
        product=product_fixture,
        quantity=2
    )

    url = reverse("orders:checkout")
    response = client.post(url, {
        "full_name": "Tester",
        "email": "a@a.com",
        "phone": "123",
        "shipping_address": "street",
        "payment_method": "cod",
    })

    assert response.status_code == 302

    order = Order.objects.first()
    assert order is not None
    assert order.total_price == 200
    assert response.url == reverse("orders:success", kwargs={"order_id": order.id})


# ============================================================================
# 2. EMPTY CART
# ============================================================================

@pytest.mark.django_db
def test_checkout_empty_cart(web_session_key):
    client = Client()

    client.cookies["sessionid"] = web_session_key

    url = reverse("orders:checkout")

    response = client.post(url, {
        "full_name": "Tester",
        "email": "a@a.com",
        "phone": "123",
        "shipping_address": "street",
        "payment_method": "cod",
    })

    assert response.status_code == 200
    assert "Корзина пуста" in response.content.decode()


# ============================================================================
# 3. NOT ENOUGH STOCK
# ============================================================================

@pytest.mark.django_db
def test_checkout_not_enough_stock(product_fixture, web_session_key):
    client = Client()

    client.cookies["sessionid"] = web_session_key

    # Устанавливаем маленький остаток
    product_fixture.stock = 1
    product_fixture.save()

    # В корзине quantity=5
    CartItem.objects.create(
        session_key=web_session_key,
        product=product_fixture,
        quantity=5
    )

    url = reverse("orders:checkout")

    response = client.post(url, {
        "full_name": "Tester",
        "email": "a@a.com",
        "phone": "123",
        "shipping_address": "street",
        "payment_method": "cod",
    })

    assert response.status_code == 200
    assert "недостаточно" in response.content.decode()
