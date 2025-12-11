from __future__ import annotations

from rest_framework import serializers

from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор отзывов.

    Используется для:
        - вывода отзывов к товару
        - создания отзыва авторизованным пользователем

    Возвращает username автора через поле user_name.
    """

    user_name: serializers.CharField = serializers.CharField(
        source="user.username",
        read_only=True,
        help_text="Имя пользователя, оставившего отзыв.",
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user",
            "user_name",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields: list[str] = [
            "id",
            "user",
            "created_at",
            "user_name",
        ]
