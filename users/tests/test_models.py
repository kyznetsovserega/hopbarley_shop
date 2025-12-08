import pytest
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()
pytestmark = pytest.mark.django_db

@pytest.mark.django_db
def test_profile_creation():
    user = User.objects.create_user(
        username="testuser",
        password="12345",
    )
    profile = user.profile

    profile.phone = "123456789"
    profile.city = "Testcity"
    profile.address = "Test ave 11"
    profile.save()

    assert  profile.user == user
    assert  profile.phone == "123456789"
    assert  profile.city == "Testcity"
    assert  profile.address == "Test ave 11"

@pytest.mark.django_db
def test_profile_str():
    user = User.objects.create_user(username="Nick",password="pass")
    profile = user.profile

    assert str(profile) == "Profile of Nick"

def test_profile_auto_created():
    """
    Проверяем, что профиль автоматически создается
    при создании User
    """
    user = User.objects.create_user(username="auto_user", password="12345")

    profile =UserProfile.objects.get(user=user)

    assert profile is not None
    assert profile.user == user
