from __future__ import annotations

from typing import Any

import pytest
from django.contrib.auth import get_user_model

from users.models import UserProfile

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_profile_creation() -> None:
    user: Any = User.objects.create_user(
        username="testuser",
        password="12345",
    )

    profile: Any = user.profile

    profile.phone = "123456789"
    profile.city = "Testcity"
    profile.address = "Test ave 11"
    profile.save()

    assert profile.user == user
    assert profile.phone == "123456789"
    assert profile.city == "Testcity"
    assert profile.address == "Test ave 11"


def test_profile_str() -> None:
    user: Any = User.objects.create_user(
        username="Nick",
        password="pass",
    )

    profile: Any = user.profile

    assert str(profile) == "Profile of Nick"


def test_profile_auto_created() -> None:
    """
    Проверяем, что профиль автоматически создается
    при создании User.
    """

    user: Any = User.objects.create_user(
        username="auto_user",
        password="12345",
    )

    profile: Any = UserProfile.objects.get(user=user)

    assert profile is not None
    assert profile.user == user
