from __future__ import annotations

from typing import Any, Dict

import pytest
from django.urls import reverse

from orders.models import Order, OrderItem
from reviews.models import Review


# ---------------------------------------------------------
# 1. Детальная страница открывается
# ---------------------------------------------------------
@pytest.mark.django_db
def test_product_detail_page_loads(
    client_web: Any,
    product_fixture: Any,
) -> None:
    url = reverse("products:product_detail", args=[product_fixture.slug])
    response = client_web.get(url)

    assert response.status_code == 200
    assert product_fixture.name in response.content.decode()


# ---------------------------------------------------------
# 2. Отзывы отображаются на странице
# ---------------------------------------------------------
@pytest.mark.django_db
def test_reviews_visible_on_product_detail(
    client_web: Any,
    review_fixture: Any,
    product_fixture: Any,
) -> None:
    url = reverse("products:product_detail", args=[product_fixture.slug])
    response = client_web.get(url)

    assert response.status_code == 200
    assert review_fixture.comment in response.content.decode()


# ---------------------------------------------------------
# 3. Пользователь НЕ авторизован > cannot review
# ---------------------------------------------------------
@pytest.mark.django_db
def test_can_review_anonymous(
    client_web: Any,
    product_fixture: Any,
) -> None:
    url = reverse("products:product_detail", args=[product_fixture.slug])
    response = client_web.get(url)

    context: Dict[str, Any] = response.context

    assert context["can_review"] is False
    assert context["already_reviewed"] is False


# ---------------------------------------------------------
# 4. Авторизован, но не покупал > can_review=False
# ---------------------------------------------------------
@pytest.mark.django_db
def test_can_review_not_purchased(
    client_web: Any,
    user_fixture: Any,
    product_fixture: Any,
) -> None:
    client_web.force_login(user_fixture)

    url = reverse("products:product_detail", args=[product_fixture.slug])
    response = client_web.get(url)

    context: Dict[str, Any] = response.context

    assert context["can_review"] is False
    assert context["already_reviewed"] is False


# ---------------------------------------------------------
# 5. После покупки (paid) > can_review=True
# ---------------------------------------------------------
@pytest.mark.django_db
def test_can_review_after_paid_purchase(
    client_web: Any,
    user_fixture: Any,
    product_fixture: Any,
) -> None:
    client_web.force_login(user_fixture)

    # создаём оплаченный заказ
    order = Order.objects.create(
        user=user_fixture,
        status="paid",
        total_price=100,
        shipping_address="Test address",
    )

    OrderItem.objects.create(
        order=order,
        product=product_fixture,
        quantity=1,
        price=product_fixture.price,
    )

    url = reverse("products:product_detail", args=[product_fixture.slug])
    response = client_web.get(url)
    context: Dict[str, Any] = response.context

    assert context["can_review"] is True
    assert context["already_reviewed"] is False


# ---------------------------------------------------------
# 6. Уже покупал и уже оставлял отзыв > can_review=False, already_reviewed=True
# ---------------------------------------------------------
@pytest.mark.django_db
def test_can_review_already_reviewed(
    client_web: Any,
    user_fixture: Any,
    product_fixture: Any,
) -> None:
    client_web.force_login(user_fixture)

    order = Order.objects.create(
        user=user_fixture,
        status="paid",
        total_price=100,
        shipping_address="Test address",
    )
    OrderItem.objects.create(
        order=order,
        product=product_fixture,
        quantity=1,
        price=product_fixture.price,
    )

    # создаём существующий отзыв
    Review.objects.create(
        user=user_fixture,
        product=product_fixture,
        rating=5,
        comment="Previous review",
    )

    url = reverse("products:product_detail", args=[product_fixture.slug])
    response = client_web.get(url)
    context: Dict[str, Any] = response.context

    assert context["can_review"] is False
    assert context["already_reviewed"] is True


# ---------------------------------------------------------
# 7. Проверка среднего рейтинга и количества отзывов
# ---------------------------------------------------------
@pytest.mark.django_db
def test_product_rating_aggregation(
    client_web: Any,
    product_fixture: Any,
    user_fixture: Any,
) -> None:
    Review.objects.create(
        product=product_fixture,
        user=user_fixture,
        rating=4,
        comment="Ok",
    )

    another_user = user_fixture.__class__.objects.create_user(
        username="another",
        email="a@a.com",
        password="12345",
    )

    Review.objects.create(
        product=product_fixture,
        user=another_user,
        rating=2,
        comment="Bad",
    )

    url = reverse("products:product_detail", args=[product_fixture.slug])
    response = client_web.get(url)
    context: Dict[str, Any] = response.context

    assert context["reviews_count"] == 2
    assert float(context["average_rating"]) == 3.0  # (4 + 2) / 2
