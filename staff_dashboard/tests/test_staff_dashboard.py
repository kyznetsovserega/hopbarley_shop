from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.crypto import get_random_string

from products.models import Product

pytestmark = pytest.mark.django_db


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def staff_user(db):
    """
    Пользователь с правами staff (не superuser).
    """
    User = get_user_model()

    user = User.objects.create_user(
        username="staffuser",
        email="staff@example.com",
        password="staffpass123",
    )
    user.is_staff = True
    user.is_superuser = False
    user.save(update_fields=["is_staff", "is_superuser"])

    return user


@pytest.fixture
def nonstaff_user(db):
    """
    Обычный пользователь без staff-прав.
    """
    User = get_user_model()

    return User.objects.create_user(
        username="plainuser",
        email="plain@example.com",
        password="plainpass123",
    )


@pytest.fixture
def staff_client(client_web, staff_user):
    """
    Клиент, залогиненный под staff-пользователем.
    """
    client_web.force_login(staff_user)
    return client_web


@pytest.fixture
def nonstaff_client(client_web, nonstaff_user):
    """
    Клиент, залогиненный под обычным пользователем.
    """
    client_web.force_login(nonstaff_user)
    return client_web


@pytest.fixture
def product_for_dashboard(category_fixture):
    """
    Товар для тестов staff dashboard.
    """
    suffix = get_random_string(6).lower()

    return Product.objects.create(
        name=f"Dash Product {suffix}",
        slug=f"dash-product-{suffix}",
        category=category_fixture,
        short_description="Short text",
        description="Long description",
        unit="1 lb",
        price="9.99",
        stock=3,
        is_active=True,
    )


# ----------------------------------------------------------------------
# Access control tests
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "url_name, kwargs",
    [
        ("staff_dashboard:home", {}),
        ("staff_dashboard:products", {}),
    ],
)
def test_dashboard_anonymous_redirects_to_users_login(
        client_web,
        url_name,
        kwargs,
):
    """
    Анонимный пользователь должен быть перенаправлен на страницу логина.
    """
    url = reverse(url_name, kwargs=kwargs)

    # follow=False — проверяем именно редирект
    response = client_web.get(url, follow=False)

    assert response.status_code == 302
    assert response["Location"].startswith("/users/login/")
    assert f"next={url}" in response["Location"]


@pytest.mark.parametrize(
    "url_name, kwargs",
    [
        ("staff_dashboard:home", {}),
        ("staff_dashboard:products", {}),
        ("staff_dashboard:product_add", {}),
    ],
)
def test_dashboard_nonstaff_gets_403(
        nonstaff_client,
        url_name,
        kwargs,
):
    """
    Обычный пользователь не имеет доступа к staff dashboard.
    """
    url = reverse(url_name, kwargs=kwargs)
    response = nonstaff_client.get(url)

    assert response.status_code == 403


@pytest.mark.parametrize(
    "url_name, kwargs",
    [
        ("staff_dashboard:home", {}),
        ("staff_dashboard:products", {}),
        ("staff_dashboard:product_add", {}),
    ],
)
def test_dashboard_staff_gets_200(
        staff_client,
        url_name,
        kwargs,
):
    """
    Staff-пользователь имеет доступ к dashboard.
    """
    url = reverse(url_name, kwargs=kwargs)
    response = staff_client.get(url)

    assert response.status_code == 200


# ----------------------------------------------------------------------
# Product CRUD tests (staff dashboard)
# ----------------------------------------------------------------------


def test_product_add_page_staff_ok(staff_client):
    """
    Страница добавления товара доступна staff-пользователю.
    """
    url = reverse("staff_dashboard:product_add")
    response = staff_client.get(url)

    assert response.status_code == 200


def test_product_add_creates_product(
        staff_client,
        category_fixture,
):
    """
    POST-запрос из dashboard создаёт новый продукт.
    """
    url = reverse("staff_dashboard:product_add")
    suffix = get_random_string(6).lower()
    name = f"New Product {suffix}"

    payload = {
        "name": name,
        "category": str(category_fixture.id),
        "short_description": "Short description",
        "description": "Full description",
        "unit": "1 lb",
        "price": "12.34",
        "stock": "5",
        "is_active": "on",
    }

    response = staff_client.post(
        url,
        data=payload,
        follow=False,
    )

    assert response.status_code == 302
    assert response["Location"] == reverse("staff_dashboard:products")
    assert Product.objects.filter(name=name).exists()


def test_product_edit_updates_product(
        staff_client,
        product_for_dashboard,
):
    """
    POST-запрос обновляет существующий продукт.
    """
    url = reverse(
        "staff_dashboard:product_edit",
        kwargs={"pk": product_for_dashboard.pk},
    )

    new_name = f"{product_for_dashboard.name} UPDATED"

    payload = {
        "name": new_name,
        "category": str(product_for_dashboard.category_id),
        "short_description": product_for_dashboard.short_description,
        "description": product_for_dashboard.description,
        "unit": product_for_dashboard.unit,
        "price": "99.99",
        "stock": str(product_for_dashboard.stock),
        "is_active": "on",
    }

    response = staff_client.post(
        url,
        data=payload,
        follow=False,
    )

    assert response.status_code == 302
    assert response["Location"] == reverse("staff_dashboard:products")

    product_for_dashboard.refresh_from_db()
    assert product_for_dashboard.name == new_name
    assert str(product_for_dashboard.price) == "99.99"


def test_product_delete_get_does_not_delete_and_redirects(
        staff_client,
        product_for_dashboard,
):
    """
    GET-запрос на удаление не удаляет продукт,
    а редиректит на страницу редактирования.
    """
    url = reverse(
        "staff_dashboard:product_delete",
        kwargs={"pk": product_for_dashboard.pk},
    )

    response = staff_client.get(url, follow=False)

    assert response.status_code == 302
    assert response["Location"] == reverse(
        "staff_dashboard:product_edit",
        kwargs={"pk": product_for_dashboard.pk},
    )
    assert Product.objects.filter(pk=product_for_dashboard.pk).exists()


def test_product_delete_post_deletes_and_redirects(
        staff_client,
        product_for_dashboard,
):
    """
    POST-запрос удаляет продукт и редиректит на список.
    """
    url = reverse(
        "staff_dashboard:product_delete",
        kwargs={"pk": product_for_dashboard.pk},
    )

    response = staff_client.post(url, follow=False)

    assert response.status_code == 302
    assert response["Location"] == reverse("staff_dashboard:products")
    assert not Product.objects.filter(pk=product_for_dashboard.pk).exists()
