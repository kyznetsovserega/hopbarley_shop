import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_profile_update(client):
    user = User.objects.create_user(
        username="john",
        email="john@example.com",
        password="StrongPass123",
        first_name="Old",
        last_name="Name"
    )

    client.login(username="john", password="StrongPass123")

    response = client.post(reverse("account"), {
        "first_name": "John",
        "last_name": "Smith",
        "email": "new@example.com",

        "phone": "+123456",
        "city": "London",
        "address": "Baker St",
        "date_of_birth": "1990-01-01",
    })

    assert response.status_code == 302

    user.refresh_from_db()
    profile = user.profile

    assert user.first_name == "John"
    assert user.last_name == "Smith"
    assert user.email == "new@example.com"

    assert profile.phone == "+123456"
    assert profile.city == "London"
    assert profile.address == "Baker St"
    assert str(profile.date_of_birth) == "1990-01-01"
