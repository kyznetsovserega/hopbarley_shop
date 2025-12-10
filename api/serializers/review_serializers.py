from rest_framework import serializers
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Review.

    Используется для:
        - вывода отзывов к товару
        - создания отзывов от имени авторизованного пользователя

    Дополнительно возвращает username автора через поле user_name.
    """

    user_name = serializers.CharField(
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
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "user_name",
        ]
