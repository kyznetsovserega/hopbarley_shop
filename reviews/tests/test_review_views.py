import pytest
from decimal import Decimal
from django.urls import reverse

from orders.models import Order, OrderItem
from reviews.models import Review


# ----------------------------
# 1. Пользователь НЕ покупал → отзыв запрещён
# ----------------------------
@pytest.mark.django_db
def test_add_review_not_purchased(client_web, product_fixture, user_fixture):
    # логиним пользователя в обычный Django-клиент
    client_web.force_login(user_fixture)

    url = reverse("reviews:add", args=[product_fixture.slug])

    response = client_web.post(url, {
        "rating": 5,
        "comment": "Should NOT work"
    })

    # редирект обратно на страницу товара
    assert response.status_code == 302

    # отзыв НЕ создан
    assert product_fixture.reviews.count() == 0


# ----------------------------
# 2. Пользователь покупал → отзыв разрешён
# ----------------------------
@pytest.mark.django_db
def test_add_review_purchased(client_web, product_fixture, user_fixture):
    client_web.force_login(user_fixture)

    # создаём успешный заказ
    order = Order.objects.create(
        user=user_fixture,
        status=Order.STATUS_PAID,  # "paid"
        total_price=Decimal("100.00"),
        shipping_address="Test address",
    )

    # создаём позицию заказа с этим продуктом
    OrderItem.objects.create(
        order=order,
        product=product_fixture,
        quantity=1,
        price=Decimal("100.00"),
    )

    url = reverse("reviews:add", args=[product_fixture.slug])

    response = client_web.post(url, {
        "rating": 4,
        "comment": "Great product",
    })

    # редирект обратно на детальную страницу товара
    assert response.status_code == 302

    # создан ровно один отзыв
    assert product_fixture.reviews.count() == 1

    review = product_fixture.reviews.first()
    assert review.rating == 4
    assert review.comment == "Great product"
    assert review.user == user_fixture


# ----------------------------
# 3. Повторный отзыв тем же пользователем → запрещён
# ----------------------------
@pytest.mark.django_db
def test_add_review_unique(client_web, product_fixture, user_fixture):
    client_web.force_login(user_fixture)

    # первый отзыв уже есть
    Review.objects.create(
        product=product_fixture,
        user=user_fixture,
        rating=5,
        comment="First review",
    )

    url = reverse("reviews:add", args=[product_fixture.slug])

    # пытаемся отправить второй отзыв
    response = client_web.post(url, {
        "rating": 3,
        "comment": "Second review",
    })

    assert response.status_code == 302

    # в базе всё ещё только один отзыв
    assert product_fixture.reviews.count() == 1

    review = product_fixture.reviews.first()
    assert review.comment == "First review"
    assert review.rating == 5
