import pytest
from django.contrib.auth.models import User
from users.models import UserProfile


@pytest.mark.django_db
def test_userprofile_created_by_signal():
    user = User.objects.create_user(
        username="john",
        email="john@example.com",
        password="12345"
    )

    assert UserProfile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_userprofile_saved_on_user_save():
    user = User.objects.create_user(
        username="john",
        email="john@example.com",
        password="12345"
    )

    # изменить email
    user.email = "new@example.com"
    user.save()

    # сигнал не должен удалить/сломать профиль
    assert user.profile is not None
    assert UserProfile.objects.filter(user=user).exists()
