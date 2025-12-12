from __future__ import annotations

from typing import Any, Dict

from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор пользователя.
    Используется для /me/, заказов, отзывов.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id", "username", "email"]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации пользователя.

    Корректно создаёт пользователя через create_user().
    """

    password: serializers.CharField = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Создание пользователя с хешированным паролем.
        """
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
