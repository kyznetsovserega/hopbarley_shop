import pytest
from reviews.models import Review

@pytest.mark.django_db
def test_review_creation(review_fixture,product_fixture,user_fixture):
    review =review_fixture

    assert isinstance(review, Review)
    assert review.product == product_fixture
    assert review.user == user_fixture
    assert  review.rating == 5
    assert review.comment == 'Отличный товар!'

    # связь с товаром
    assert product_fixture.reviews.count() == 1
    assert product_fixture.reviews.first() == review

@pytest.mark.django_db
def test_review_str(review_fixture):
    text = str(review_fixture)
    assert 'testuser' in text
    assert 'Тестовый продукт' in text
    assert  '5/5' in text
