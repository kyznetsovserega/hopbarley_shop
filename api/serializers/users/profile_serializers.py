from __future__ import annotations

from rest_framework import serializers

from users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя.

    Возвращает основную контактную информацию:
        - phone — номер телефона
        - city — город проживания
        - address — адрес доставки
        - date_of_birth — дата рождения (опционально)
    """

    phone: serializers.CharField = serializers.CharField()
    city: serializers.CharField = serializers.CharField()
    address: serializers.CharField = serializers.CharField()
    date_of_birth: serializers.DateField = serializers.DateField(required=False)

    class Meta:
        model = UserProfile
        fields = [
            "phone",
            "city",
            "address",
            "date_of_birth",
        ]
        read_only_fields: list[str] = []
