import pytest

from products.models import Category, Product


@pytest.mark.django_db
def test_create_product(product_fixture, category_fixture):
    product = product_fixture
    category = category_fixture

    assert product.name =='Тестовый продукт'
    assert product.category.name == 'Тестовая категория'
    assert category.slug == 'test-category'
    assert product.slug == 'test-product'


@pytest.mark.django_db
def test_category_models(category_fixture):
    category = category_fixture

    assert category.name =='Тестовая категория'
    assert category.slug == 'test-category'
    assert category.parent is None
    assert category.get_absolute_url().endswith("?category=test-category")

@pytest.mark.django_db
def test_product_model(product_fixture):
    product = product_fixture

    # Данные из фикстуры
    assert product.name == "Тестовый продукт"
    assert product.slug == "test-product"
    assert product.price > 0

    # Связи
    assert product.category is not None

    # URL
    assert product.get_absolute_url().endswith("/product/test-product/")

@pytest.mark.django_db
def test_product_discount():
    category = Category.objects.create(name="Cat", slug="cat")
    product = Product.objects.create(
        name="Дисконт",
        price=80,
        old_price=100,
        category=category
    )

    assert product.is_discounted is True
    assert product.discount_percent == 20
