import pytest


@pytest.mark.django_db
def test_create_product(product_fixture, category_fixture):
    product = product_fixture
    category = category_fixture

    assert product.name =='Тестовый продукт'
    assert product.category.name == 'Тестовая категория'
    assert category.slug == 'test-category'
    assert product.slug == 'test-product'