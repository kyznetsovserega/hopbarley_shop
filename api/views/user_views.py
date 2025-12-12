from __future__ import annotations

from typing import Any, Dict, List

from django.contrib.auth import login
from drf_spectacular.utils import OpenApiExample, OpenApiRequest, OpenApiResponse, extend_schema
from rest_framework import permissions, status, views
from rest_framework.request import Request
from rest_framework.response import Response

from api.serializers.users.profile_serializers import UserProfileSerializer
from api.serializers.users.user_serializers import RegisterSerializer, UserSerializer
from cart.utils import merge_session_cart_into_user_cart


# ======================================================================
# REGISTER — создание пользователя + перенос корзины
# ======================================================================
@extend_schema(
    tags=["Users"],
    summary="Регистрация нового пользователя",
    description=("Создаёт нового пользователя, выполняет автоматический вход " "и переносит корзину из сессии."),
    request=OpenApiRequest(
        request=Dict[str, Any],
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
        201: OpenApiResponse(response=UserSerializer),
        400: OpenApiResponse(description="Ошибка регистрации."),
    },
)
class RegisterView(views.APIView):
    permission_classes: List[type[permissions.BasePermission]] = [permissions.AllowAny]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # session login
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
    responses={
        200: OpenApiResponse(
            response=Dict[str, Any],
            description="Данные текущего пользователя.",
        ),
        401: OpenApiResponse(description="Требуется авторизация."),
    },
)
class MeView(views.APIView):
    permission_classes: List[type[permissions.BasePermission]] = [permissions.IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
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
    summary="Обновить данные профиля",
    description="Атомарное обновление User + UserProfile.",
    request=OpenApiRequest(
        request=Dict[str, Any],
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
        200: OpenApiResponse(description="Данные успешно обновлены."),
        400: OpenApiResponse(description="Ошибка валидации."),
        401: OpenApiResponse(description="Требуется авторизация."),
    },
)
class UpdateProfileView(views.APIView):
    permission_classes: List[type[permissions.BasePermission]] = [permissions.IsAuthenticated]

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        profile = user.profile

        data: Dict[str, Any] = request.data

        # разделяем user / profile
        user_data: Dict[str, Any] = data.get("user", {})
        profile_data: Dict[str, Any] = data.get("profile", {})

        user_serializer = UserSerializer(user, data=user_data, partial=True)
        profile_serializer = UserProfileSerializer(profile, data=profile_data, partial=True)

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
