import pytest
from django.contrib.auth import get_user_model
from products.models import Category, Product
from reviews.models import Review
from django.test import Client
from rest_framework.test import APIClient


# ------------------------------
# USERS
# ------------------------------
@pytest.fixture
def user_fixture(db):
    """ Создает тестового пользователя """
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
    )


@pytest.fixture
def profile_fixture(db, user_fixture):
    from users.models import UserProfile
    return UserProfile.objects.create(user=user_fixture)


# ------------------------------
# Products
# ------------------------------
@pytest.fixture
def category_fixture(db):
    """ Создает тестовую категорию """
    return Category.objects.create(
        name='Тестовая категория',
        slug='test-category'
    )


@pytest.fixture
def product_fixture(db, category_fixture):
    """ Создает тестовый продукт, связанный с категорией """
    return Product.objects.create(
        name='Тестовый продукт',
        slug='test-product',
        description='Описание товара',
        price=100.0,
        category=category_fixture,
        stock=10,
        is_active=True
    )


# ------------------------------
# REVIEWS
# ------------------------------
@pytest.fixture
def review_fixture(db, user_fixture, product_fixture):
    """ Создает тестовый отзыв к тестовому продукту """
    return Review.objects.create(
        product=product_fixture,
        user=user_fixture,
        rating=5,
        comment='Отличный товар!',
    )


# ------------------------------
# ORDERS
# ------------------------------

@pytest.fixture
def order_fixture(db, user_fixture):
    from orders.models import Order
    return Order.objects.create(
        user=user_fixture,
        status='pending',
        total_price=0,
        shipping_address='Тестовый адрес',
    )


@pytest.fixture
def order_item_fixture(db, order_fixture, product_fixture):
    from orders.models import OrderItem
    return OrderItem.objects.create(
        order=order_fixture,
        product=product_fixture,
        quantity=2,
        price=product_fixture.price
    )


# ------------------------------
# API
# ------------------------------

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(client, user_fixture):
    """клиент с авторизацией"""
    client.force_authenticate(user=user_fixture)
    return client


# ------------------------------
# SESSION
# ------------------------------
@pytest.fixture
def session_key(client):
    """Создаёт session_key для тестов"""
    session = client.session
    session.create()
    session.save()
    return session.session_key


# ------------------------------
# CART
# ------------------------------
@pytest.fixture
def cart_item_fixture(db, session_key, product_fixture):
    """Создаёт CartItem для тестов"""
    from cart.models import CartItem
    return CartItem.objects.create(
        session_key=session_key,
        product=product_fixture,
        quantity=2
    )


# ------------------------------
# WEB CLIENT (для checkout)
# ------------------------------
@pytest.fixture
def client_web(db):
    return Client()


# ------------------------------
# API CLIENT (для API-тестов)
# ------------------------------
@pytest.fixture
def client_api():
    return APIClient()


# ------------------------------
# SESSION для WEB-тестов
# ------------------------------
@pytest.fixture
def web_session_key(client_web):
    session = client_web.session
    session.create()
    session.save()
    return session.session_key
