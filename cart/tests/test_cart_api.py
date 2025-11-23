from http.client import responses

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestCartAPI:

    @pytest.fixture
    def cart_url(self):
        """url списка корзины от DefaultRouter"""
        return reverse("cartitem-list")

    def test_add_to_cart(self, auth_client, product_fixture,user_fixture,cart_url):
        response = auth_client.post(cart_url, {
            "product": product_fixture.id,
            "quantity": 2
        }, format="json")

        assert response.status_code == 201
        assert response.data["quantity"]== 2
        assert response.data["product"]== product_fixture.id

    def test_get_cart_items(self, auth_client,product_fixture,user_fixture, cart_url):
        from cart.models import CartItem
        CartItem.objects.create(user=user_fixture, product=product_fixture, quantity=1)

        response = auth_client.get(cart_url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["product"] == product_fixture.id

    def test_update_quantity(self,auth_client,product_fixture,user_fixture):
        from cart.models import CartItem
        item = CartItem.objects.create(
            user=user_fixture,
            product=product_fixture,
            quantity=1
        )

        url = reverse("cartitem-detail",args=[item.id])

        response = auth_client.patch(url, {"quantity": 5}, format="json")

        assert response.status_code == 200
        assert response.data["quantity"] == 5

    def test_delete_item(self,auth_client,product_fixture,user_fixture):
        from cart.models import CartItem
        item = CartItem.objects.create(
            user=user_fixture,
            product=product_fixture,
            quantity=1
        )

        url = reverse("cartitem-detail",args=[item.id])

        response = auth_client.delete(url)

        assert response.status_code == 204



