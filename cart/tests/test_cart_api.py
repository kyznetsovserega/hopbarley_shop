from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestCartAPI:

    @pytest.fixture
    def cart_url(self) -> str:
        return reverse("cartitem-list")

    # ---------------------------------------------------------
    # 1. Добавление товара в корзину
    # ---------------------------------------------------------
    def test_add_to_cart(
        self,
        auth_client: Any,
        product_fixture: Any,
        cart_url: str,
    ) -> None:
        response = auth_client.post(
            cart_url,
            {"product": product_fixture.id, "quantity": 2},
            format="json",
        )

        assert response.status_code == 201
        assert response.data["quantity"] == 2
        assert response.data["product"] == product_fixture.id
        assert "total_price" in response.data

        # повторное добавление > количество увеличивается
        response2 = auth_client.post(
            cart_url,
            {"product": product_fixture.id, "quantity": 3},
            format="json",
        )

        assert response2.status_code == 201
        assert response2.data["quantity"] == 5  # 2 + 3

    # ---------------------------------------------------------
    # 2. Получение списка корзины
    # ---------------------------------------------------------
    def test_get_cart_items(
        self,
        auth_client: Any,
        user_cart_item_fixture: Any,
        product_fixture: Any,
        cart_url: str,
    ) -> None:
        response = auth_client.get(cart_url)
        assert response.status_code == 200

        # API возвращает список объектов
        assert len(response.data) == 1
        assert response.data[0]["product"] == product_fixture.id

    # ---------------------------------------------------------
    # 3. Изменение количества товара
    # ---------------------------------------------------------
    def test_update_quantity(
        self,
        auth_client: Any,
        product_fixture: Any,
        user_fixture: Any,
    ) -> None:
        from cart.models import CartItem

        item = CartItem.objects.create(
            user=user_fixture,
            product=product_fixture,
            quantity=1,
        )

        url = reverse("cartitem-detail", args=[item.id])

        response = auth_client.patch(url, {"quantity": 5}, format="json")

        assert response.status_code == 200
        assert response.data["quantity"] == 5
        assert float(response.data["total_price"]) == product_fixture.price * 5

    # ---------------------------------------------------------
    # 4. Удаление элемента корзины
    # ---------------------------------------------------------
    def test_delete_item(
        self,
        auth_client: Any,
        user_fixture: Any,
        product_fixture: Any,
    ) -> None:
        from cart.models import CartItem

        item = CartItem.objects.create(
            user=user_fixture,
            product=product_fixture,
            quantity=1,
        )

        url = reverse("cartitem-detail", args=[item.id])
        response = auth_client.delete(url)

        assert response.status_code == 204
        assert CartItem.objects.count() == 0
