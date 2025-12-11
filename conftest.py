import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Category
from products.models import Product
from reviews.models import Review

# ======================================================================
# USERS
# ======================================================================


@pytest.fixture
def user_fixture(db):
    """Создаёт тестового пользователя (профиль создаётся сигналом)."""
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


# ======================================================================
# PRODUCTS
# ======================================================================


@pytest.fixture
def category_fixture(db):
    return Category.objects.create(
        name="Тестовая категория",
        slug="test-category",
    )


@pytest.fixture
def product_fixture(db, category_fixture):
    return Product.objects.create(
        name="Тестовый продукт",
        slug="test-product",
        description="Описание товара",
        price=100.00,
        category=category_fixture,
        stock=10,
        is_active=True,
    )


# ======================================================================
# REVIEWS
# ======================================================================


@pytest.fixture
def review_fixture(db, user_fixture, product_fixture):
    """Готовый отзыв (используется для тестов списка)."""
    return Review.objects.create(
        product=product_fixture,
        user=user_fixture,
        rating=5,
        comment="Отличный товар!",
    )


# ======================================================================
# ORDERS
# ======================================================================


@pytest.fixture
def order_fixture(db, user_fixture):
    """Базовый заказ (по умолчанию pending)."""
    from orders.models import Order

    return Order.objects.create(
        user=user_fixture,
        status="pending",
        total_price=0,
        shipping_address="Тестовый адрес",
    )


@pytest.fixture
def order_item_fixture(db, order_fixture, product_fixture):
    """Item заказа — НЕ делает покупку завершённой."""
    from orders.models import OrderItem

    return OrderItem.objects.create(
        order=order_fixture,
        product=product_fixture,
        quantity=2,
        price=product_fixture.price,
    )


# === ДОПОЛНИТЕЛЬНЫЕ ФИКСТУРЫ ДЛЯ TEST REVIEWS ===


@pytest.fixture
def paid_order_fixture(order_fixture):
    """Заказ со статусом paid — разрешает оставить отзыв."""
    order_fixture.status = "paid"
    order_fixture.save()
    return order_fixture


@pytest.fixture
def delivered_order_fixture(order_fixture):
    """Заказ со статусом delivered — тоже разрешает отзыв."""
    order_fixture.status = "delivered"
    order_fixture.save()
    return order_fixture


@pytest.fixture
def paid_order_item_fixture(db, paid_order_fixture, product_fixture):
    """Товар в оплачённом заказе — завершённая покупка."""
    from orders.models import OrderItem

    return OrderItem.objects.create(
        order=paid_order_fixture,
        product=product_fixture,
        quantity=1,
        price=product_fixture.price,
    )


# ======================================================================
# EMAIL SETTINGS
# ======================================================================


@pytest.fixture(autouse=True)
def email_settings(settings):
    settings.DEFAULT_FROM_EMAIL = "noreply@test.com"
    settings.ADMIN_EMAIL = "admin@test.com"


# ======================================================================
# CHECKOUT POST HELPER
# ======================================================================


@pytest.fixture
def checkout_post(client_web, web_session_key):
    def do_post(data):
        client_web.cookies["sessionid"] = web_session_key
        return client_web.post(reverse("orders:checkout"), data)

    return do_post


# ======================================================================
# API CLIENTS
# ======================================================================


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(client, user_fixture):
    client.force_authenticate(user=user_fixture)
    return client


@pytest.fixture
def auth_client_with_cart(auth_client, user_cart_item_fixture):
    return auth_client


@pytest.fixture
def client_api():
    return APIClient()


# ======================================================================
# SESSION FIXTURES
# ======================================================================


@pytest.fixture
def session_key(client):
    session = client.session
    session.create()
    session.save()
    return session.session_key


@pytest.fixture
def web_session_key(client_web):
    session = client_web.session
    session.create()
    session.save()
    return session.session_key


# ======================================================================
# CART FIXTURES
# ======================================================================


@pytest.fixture
def cart_item_fixture(db, session_key, product_fixture):
    from cart.models import CartItem

    return CartItem.objects.create(
        session_key=session_key,
        product=product_fixture,
        quantity=2,
    )


@pytest.fixture
def user_cart_item_fixture(db, user_fixture, product_fixture):
    from cart.models import CartItem

    return CartItem.objects.create(
        user=user_fixture,
        product=product_fixture,
        quantity=2,
    )


# ======================================================================
# WEB CLIENT
# ======================================================================


@pytest.fixture
def client_web(db):
    return Client()
