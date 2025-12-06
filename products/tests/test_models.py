"""
Тесты моделей Category и Product.
Покрывают: slug, URL, связи, скидки, генерацию тегов.
"""

import pytest
from products.models import Category, Product


@pytest.mark.django_db
class TestCategory:
    def test_category_creation(self, category_fixture):
        category = category_fixture

        assert category.name == "Тестовая категория"
        assert category.slug == "test-category"
        assert category.parent is None

    def test_category_url(self, category_fixture):
        category = category_fixture
        assert category.get_absolute_url().endswith("?category=test-category")


@pytest.mark.django_db
class TestProduct:
    def test_product_creation(self, product_fixture):
        product = product_fixture

        assert product.name == "Тестовый продукт"
        assert product.slug == "test-product"
        assert product.price > 0
        assert product.category is not None

    def test_product_url(self, product_fixture):
        product = product_fixture
        assert product.get_absolute_url().endswith("/products/test-product/")

    def test_product_default_flags(self, product_fixture):
        product = product_fixture
        assert product.is_active is True
        assert product.stock >= 0

    def test_tags_generated_from_short_description(self):
        category = Category.objects.create(name="Test", slug="test")
        product = Product.objects.create(
            name="Тест тегов",
            short_description="Ароматный свежий солод",
            description="desc",
            price=10,
            category=category,
        )

        assert product.tags != ""
        assert "ароматный" in product.tags or "свежий" in product.tags


@pytest.mark.django_db
class TestProductDiscount:
    def test_product_discount_logic(self):
        category = Category.objects.create(name="Cat", slug="cat")
        product = Product.objects.create(
            name="Дисконт",
            price=80,
            old_price=100,
            category=category,
        )

        assert product.is_discounted is True
        assert product.discount_percent == 20
