from __future__ import annotations

from typing import Any

import pytest
from django.core.exceptions import ValidationError

from reviews.models import Review


# --------------------------------------------------------
# 1. Создание отзыва
# --------------------------------------------------------
@pytest.mark.django_db
def test_review_creation(
    review_fixture: Any,
    product_fixture: Any,
    user_fixture: Any,
) -> None:
    review = review_fixture

    assert isinstance(review, Review)
    assert review.product == product_fixture
    assert review.user == user_fixture
    assert review.rating == 5
    assert review.comment == "Отличный товар!"

    # связь с продуктом
    assert product_fixture.reviews.count() == 1

    first = product_fixture.reviews.first()
    assert first is not None
    assert first == review


# --------------------------------------------------------
# 2. Строковое представление (__str__)
# --------------------------------------------------------
@pytest.mark.django_db
def test_review_str(
    review_fixture: Any,
) -> None:
    text = str(review_fixture)

    assert "testuser" in text
    assert review_fixture.product.name in text
    assert "(5/5)" in text


# --------------------------------------------------------
# 3. Уникальность: нет двух отзывов от одного пользователя к одному товару
# --------------------------------------------------------
@pytest.mark.django_db
def test_review_unique_constraint(
    user_fixture: Any,
    product_fixture: Any,
) -> None:
    Review.objects.create(
        user=user_fixture,
        product=product_fixture,
        rating=4,
        comment="Первый",
    )

    with pytest.raises(Exception):
        Review.objects.create(
            user=user_fixture,
            product=product_fixture,
            rating=5,
            comment="Второй",
        )


# --------------------------------------------------------
# 4. Валидация рейтинга (clean)
# --------------------------------------------------------
@pytest.mark.django_db
def test_review_rating_validation(
    user_fixture: Any,
    product_fixture: Any,
) -> None:
    review = Review(
        user=user_fixture,
        product=product_fixture,
        rating=10,  # недопустимый рейтинг
        comment="Invalid rating",
    )

    with pytest.raises(ValidationError):
        review.clean()
