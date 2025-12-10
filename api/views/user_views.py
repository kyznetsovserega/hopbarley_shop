from __future__ import annotations

from django.contrib.auth import login
from rest_framework import permissions, status, views
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiRequest,
    OpenApiResponse,
)

from api.serializers.users.user_serializers import (
    UserSerializer,
    RegisterSerializer,
)
from api.serializers.users.profile_serializers import UserProfileSerializer
from cart.utils import merge_session_cart_into_user_cart


# ======================================================================
# REGISTER — создание пользователя + перенос корзины
# ======================================================================
@extend_schema(
    tags=["Users"],
    summary="Регистрация нового пользователя",
    description=(
        "Создаёт нового пользователя, выполняет автоматический вход "
        "и переносит корзину из сессии.\n\n"
        "**Используется для WEB-регистрации.**\n\n"
        "**Что происходит:**\n"
        "- Проверка данных\n"
        "- Создание пользователя\n"
        "- Session-based login\n"
        "- Перенос корзины (если есть session_key)"
    ),
    request=OpenApiRequest(
        request=dict,
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "username": "sergey",
                    "email": "sergey@example.com",
                    "password": "12345678",
                },
            )
        ],
    ),
    responses={
        201: OpenApiResponse(
            response=UserSerializer,
            description="Пользователь успешно зарегистрирован.",
        ),
        400: OpenApiResponse(
            description="Ошибка регистрации.",
            examples=[
                OpenApiExample(
                    "Некорректные данные",
                    value={"email": ["Введите корректный адрес."]},
                )
            ],
        ),
    },
)
class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # Вход (session login)
        login(request, user)

        # перенос корзины
        session_key = request.session.session_key
        if session_key:
            merge_session_cart_into_user_cart(user, session_key)

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


# ======================================================================
# ME — получение текущего пользователя
# ======================================================================
@extend_schema(
    tags=["Users"],
    summary="Получить данные текущего пользователя",
    description=(
        "Возвращает информацию о текущем пользователе.\n\n"
        "**Требуется JWT-аутентификация.**\n\n"
        "Ответ включает:\n"
        "- данные модели User\n"
        "- данные модели UserProfile"
    ),
    responses={
        200: OpenApiResponse(
            description="Данные пользователя успешно получены.",
            examples=[
                OpenApiExample(
                    "Пример ответа",
                    value={
                        "user": {
                            "id": 4,
                            "username": "sergey",
                            "email": "sergey@example.com",
                            "first_name": "",
                            "last_name": "",
                        },
                        "profile": {
                            "phone": "+1234567",
                            "city": "Moscow",
                            "address": "Red Square, 1",
                            "date_of_birth": "1990-10-10",
                        },
                    },
                )
            ],
        ),
        401: OpenApiResponse(description="Требуется авторизация."),
    },
)
class MeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request) -> Response:
        user = request.user
        return Response(
            {
                "user": UserSerializer(user).data,
                "profile": UserProfileSerializer(user.profile).data,
            }
        )


# ======================================================================
# UPDATE PROFILE — обновление User + UserProfile
# ======================================================================
@extend_schema(
    tags=["Users"],
    summary="Обновить данные профиля пользователя",
    description=(
        "Позволяет обновить данные модели User и UserProfile.\n\n"
        "**Требуется JWT-аутентификация.**\n\n"
        "Изменения применяются атомарно: если сериализатор User или "
        "UserProfile не проходит валидацию, возвращается ошибка обоих."
    ),
    request=OpenApiRequest(
        request=dict,
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "user": {
                        "first_name": "Sergey",
                        "last_name": "Kuznetsov",
                        "email": "sergey@example.com",
                    },
                    "profile": {
                        "phone": "+1234567",
                        "city": "Moscow",
                        "address": "Lenina 15",
                        "date_of_birth": "1990-10-10",
                    },
                },
            )
        ],
    ),
    responses={
        200: OpenApiResponse(
            description="Данные успешно обновлены.",
        ),
        400: OpenApiResponse(
            description="Ошибка валидации.",
            examples=[
                OpenApiExample(
                    "Пример ошибки",
                    value={
                        "user_errors": {"email": ["Этот email уже используется."]},
                        "profile_errors": {"phone": ["Некорректный формат номера."]},
                    },
                )
            ],
        ),
        401: OpenApiResponse(description="Требуется авторизация."),
    },
)
class UpdateProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request) -> Response:
        user = request.user
        profile = user.profile

        # Разделяем входящие данные
        user_data = request.data.get("user", {})
        profile_data = request.data.get("profile", {})

        user_serializer = UserSerializer(
            user, data=user_data, partial=True
        )
        profile_serializer = UserProfileSerializer(
            profile, data=profile_data, partial=True
        )

        user_valid = user_serializer.is_valid()
        profile_valid = profile_serializer.is_valid()

        if user_valid and profile_valid:
            user_serializer.save()
            profile_serializer.save()

            return Response(
                {
                    "user": user_serializer.data,
                    "profile": profile_serializer.data,
                }
            )

        return Response(
            {
                "user_errors": user_serializer.errors,
                "profile_errors": profile_serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
