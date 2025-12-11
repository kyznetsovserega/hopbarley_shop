from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from users.models import UserProfile


@pytest.mark.django_db
def test_user_registration(client: Any) -> None:
    url = reverse("users:register")

    response = client.post(
        url,
        {
            "username": "john",
            "email": "john@example.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        },
    )

    # редирект после успешной регистрации
    assert response.status_code == 302

    # пользователь создан
    user: Any = User.objects.get(username="john")
    assert user.email == "john@example.com"

    # профиль создан автоматически
    assert UserProfile.objects.filter(user=user).exists()
