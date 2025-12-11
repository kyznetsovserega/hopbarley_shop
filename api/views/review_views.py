from __future__ import annotations

from drf_spectacular.utils import OpenApiExample, OpenApiRequest, OpenApiResponse, extend_schema
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError

from api.serializers.review_serializers import ReviewSerializer
from orders.models import Order
from reviews.models import Review


@extend_schema(
    tags=["Reviews"],
    summary="Отзывы о товарах",
    description=(
        "API для работы с отзывами.\n\n"
        "**Возможности:**\n"
        "- Получение списка отзывов по товару (`?product=<id>`)\n"
        "- Добавление нового отзыва (только после покупки)\n"
        "- Обновление и удаление отзыва (только автор)\n\n"
        "**Правила:**\n"
        "- Один пользователь может оставить ОДИН отзыв на товар\n"
        "- Оставлять отзыв могут только пользователи, купившие товар\n"
        "- Отзывы отсортированы по дате"
    ),
)
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # ----------------------------------------------------------------------
    # GET /api/reviews/?product=<id>
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Получить отзывы по товару",
        description=(
            "Фильтрует отзывы по параметру `?product=<id>`.\n\n"
            "Если параметр не указан > возвращает пустой список.\n\n"
            "Пример:\n"
            "`/api/reviews/?product=1`"
        ),
        responses={
            200: OpenApiResponse(
                response=ReviewSerializer(many=True),
                description="Отзывы успешно получены.",
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value=[
                            {
                                "id": 12,
                                "product": 1,
                                "user": 4,
                                "user_name": "sergey",
                                "rating": 5,
                                "comment": "Отличный хмель!",
                                "created_at": "2025-01-10T12:33:00Z",
                            }
                        ],
                    )
                ],
            )
        },
    )
    def get_queryset(self):
        product_id = self.request.query_params.get("product")

        if not product_id:
            return Review.objects.none()

        return Review.objects.filter(product_id=product_id).select_related("user", "product").order_by("-created_at")

    # ----------------------------------------------------------------------
    # POST /api/reviews/
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Создать отзыв",
        description=(
            "Создаёт отзыв о товаре.\n\n"
            "**Условия:**\n"
            "- Пользователь должен быть авторизован\n"
            "- Должен иметь заказ со статусом `paid` или `delivered`\n"
            "- Может оставить только один отзыв на товар\n\n"
            "Пример запроса:"
        ),
        request=OpenApiRequest(
            request=dict,
            examples=[
                OpenApiExample(
                    "Пример запроса",
                    value={
                        "product": 1,
                        "rating": 5,
                        "comment": "Отличный товар!",
                    },
                )
            ],
        ),
        responses={
            201: OpenApiResponse(
                response=ReviewSerializer,
                description="Отзыв успешно создан.",
            ),
            400: OpenApiResponse(
                description="Ошибка создания отзыва.",
                examples=[
                    OpenApiExample(
                        "Пользователь не покупал товар",
                        value={
                            "detail": ("Оставлять отзывы могут только пользователи, " "которые покупали этот товар.")
                        },
                    ),
                    OpenApiExample(
                        "Отзыв уже существует",
                        value={"detail": "Вы уже оставили отзыв на этот товар."},
                    ),
                ],
            ),
        },
    )
    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data["product"]

        # Проверяем факт покупки
        has_bought = Order.objects.filter(
            user=user,
            items__product=product,
            status__in=["paid", "delivered"],
        ).exists()

        if not has_bought:
            raise ValidationError("Оставлять отзывы могут только пользователи, " "которые покупали этот товар.")

        # Проверяем повторный отзыв
        if Review.objects.filter(user=user, product=product).exists():
            raise ValidationError("Вы уже оставили отзыв на этот товар.")

        serializer.save(user=user)

    # ----------------------------------------------------------------------
    # UPDATE / DELETE — только автор
    # ----------------------------------------------------------------------
    @extend_schema(
        summary="Обновить отзыв",
        description="Позволяет изменить свой отзыв. Другие пользователи — 403.",
    )
    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            raise ValidationError("Вы можете изменять только свои отзывы.")
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить отзыв",
        description="Удаляет отзыв. Только автор отзыва имеет доступ.",
    )
    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            raise ValidationError("Вы можете удалять только свои отзывы.")
        return super().destroy(request, *args, **kwargs)
