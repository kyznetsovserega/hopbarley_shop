import pytest
from orders.models import Order, OrderItem

@pytest.mark.django_db
def test_review_creation(order_fixture, user_fixture):
    order =order_fixture
    assert isinstance(order,Order)
    assert order.user == user_fixture
    assert order.status == 'pending'
    assert order.shipping_address == 'Тестовый адрес'

@pytest.mark.django_db
def test_order_item_creation(order_item_fixture,product_fixture,order_fixture):
    item = order_item_fixture
    assert isinstance(item,OrderItem)
    assert item.order == order_fixture
    assert item.product == product_fixture
    assert item.quantity == 2
    assert item.price == product_fixture.price

    # проверка связей
    assert order_fixture.items.count() == 1
    assert product_fixture.order_items.count() == 1
