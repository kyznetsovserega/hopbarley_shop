from __future__ import annotations

import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from users.models import UserProfile

User = get_user_model()


class UserProfileType(DjangoObjectType):
    """
    GraphQL тип профиля пользователя.
    """

    full_address = graphene.String(description="Formatted full address (city + address).")

    class Meta:
        model = UserProfile
        fields = (
            "phone",
            "city",
            "address",
            "date_of_birth",
            "created_at",
            "updated_at",
        )
        description = "Extended user profile."

    def resolve_full_address(self, info) -> str:
        return self.get_full_address()


class UserType(DjangoObjectType):
    """
    GraphQL тип пользователя.
    """

    profile = graphene.Field(UserProfileType)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
        )
        description = "Authenticated user."

    def resolve_profile(self, info) -> UserProfile:
        # profile всегда существует по signal
        return self.profile
