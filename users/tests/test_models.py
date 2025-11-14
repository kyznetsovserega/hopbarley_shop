import pytest
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()

@pytest.mark.django_db
def test_profile_creation():
    user = User.objects.create_user(
        username="testuser",
        password="12345",
    )
    profile = UserProfile.objects.create(
        user = user,
        phone = "123456789",
        city = "Testcity",
        address = "Test ave 11",
    )

    assert  profile.user == user
    assert  profile.phone == "123456789"
    assert  profile.city == "Testcity"
    assert  profile.address == "Test ave 11"

@pytest.mark.django_db
def test_profile_str():
    user = User.objects.create_user(username="Nick",password="pass")
    profile = UserProfile.objects.create(user=user)

    assert str(profile) == "Profile of Nick"