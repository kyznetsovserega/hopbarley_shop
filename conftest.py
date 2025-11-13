import pytest
from django.contrib.auth import get_user_model
from django.template.defaulttags import comment

from shop.models import Category, Product
from reviews.models import Review


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


# ------------------------------
# SHOP
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
        slug = 'test-product',
        description = 'Описание товара',
        price = 100.0,
        category = category_fixture,
        stock = 10,
        is_active = True
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












