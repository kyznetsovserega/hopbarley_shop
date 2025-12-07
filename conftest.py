import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from rest_framework.test import APIClient

from products.models import Category, Product
from reviews.models import Review


# ============================================================================
# USERS
# ============================================================================

@pytest.fixture
def user_fixture(db):
    """Создаёт тестового пользователя."""
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def profile_fixture(db, user_fixture):
    """Создаёт профиль пользователя."""
    from users.models import UserProfile
    return UserProfile.objects.create(user=user_fixture)


# ============================================================================
# PRODUCTS
# ============================================================================

@pytest.fixture
def category_fixture(db):
    """Создаёт тестовую категорию."""
    return Category.objects.create(
        name="Тестовая категория",
        slug="test-category",
    )


@pytest.fixture
def product_fixture(db, category_fixture):
    """Создаёт тестовый продукт с ценой и остатком."""
    return Product.objects.create(
        name="Тестовый продукт",
        slug="test-product",
        description="Описание товара",
        price=100.00,
        category=category_fixture,
        stock=10,
        is_active=True,
    )


# ============================================================================
# REVIEWS
# ============================================================================

@pytest.fixture
def review_fixture(db, user_fixture, product_fixture):
    """Создаёт тестовый отзыв."""
    return Review.objects.create(
        product=product_fixture,
        user=user_fixture,
        rating=5,
        comment="Отличный товар!",
    )


# ============================================================================
# ORDERS
# ============================================================================

@pytest.fixture
def order_fixture(db, user_fixture):
    """Создаёт тестовый заказ."""
    from orders.models import Order
    return Order.objects.create(
        user=user_fixture,
        status="pending",
        total_price=0,
        shipping_address="Тестовый адрес",
    )


@pytest.fixture
def order_item_fixture(db, order_fixture, product_fixture):
    """Создаёт товар внутри заказа."""
    from orders.models import OrderItem
    return OrderItem.objects.create(
        order=order_fixture,
        product=product_fixture,
        quantity=2,
        price=product_fixture.price,
    )


# ---- Настройки email для тестов (нужно для send_mail) ----

@pytest.fixture(autouse=True)
def email_settings(settings):
    """Автоматически переопределяет email-настройки для всех тестов."""
    settings.DEFAULT_FROM_EMAIL = "noreply@test.com"
    settings.ADMIN_EMAIL = "admin@test.com"


# ---- Упрощённый вызов checkout в тестах ----

@pytest.fixture
def checkout_post(client_web, web_session_key):
    """
    checkout_post(data) > делает POST на /checkout/ с учётом session_key.
    """
    def do_post(data):
        client_web.cookies["sessionid"] = web_session_key
        return client_web.post(reverse("orders:checkout"), data)
    return do_post


# ============================================================================
# API CLIENTS
# ============================================================================

@pytest.fixture
def client():
    """APIClient для API-тестов."""
    return APIClient()


@pytest.fixture
def auth_client(client, user_fixture):
    """APIClient с авторизованным пользователем."""
    client.force_authenticate(user=user_fixture)
    return client


@pytest.fixture
def client_api():
    """Альтернативный API client."""
    return APIClient()


# ============================================================================
# SESSIONS
# ============================================================================

@pytest.fixture
def session_key(client):
    """Создаёт session_key для API тестов."""
    session = client.session
    session.create()
    session.save()
    return session.session_key


@pytest.fixture
def web_session_key(client_web):
    """Создаёт session_key для web-тестов (Django Client)."""
    session = client_web.session
    session.create()
    session.save()
    return session.session_key


# ============================================================================
# CART
# ============================================================================

@pytest.fixture
def cart_item_fixture(db, session_key, product_fixture):
    """Создаёт CartItem."""
    from cart.models import CartItem
    return CartItem.objects.create(
        session_key=session_key,
        product=product_fixture,
        quantity=2,
    )


# ============================================================================
# WEB CLIENT
# ============================================================================

@pytest.fixture
def client_web(db):
    """Django Client для web-тестов."""
    return Client()
