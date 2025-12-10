from __future__ import annotations

from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор данных пользователя.

    Используется:
        - в эндпоинте /me/
        - при выводе связанных данных (например, в отзывах или заказах)

    Возвращает базовую информацию о пользователе.
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
    Сериализатор для регистрации пользователя.

    Обрабатывает:
        - username
        - email
        - password (write_only)

    Создаёт пользователя с корректным хешированием пароля.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data: dict) -> User:
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
