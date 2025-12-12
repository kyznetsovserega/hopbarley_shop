from __future__ import annotations

import graphene
from graphene import ResolveInfo

from graphql_api.types.user_types import UserProfileType, UserType


class UserQuery(graphene.ObjectType):
    """
    GraphQL-запросы пользователя.
    """

    me = graphene.Field(
        UserType,
        description="Returns current authenticated user.",
    )

    my_profile = graphene.Field(
        UserProfileType,
        description="Returns current user's profile.",
    )

    # ---------------------------------------------------------
    def resolve_me(self, info: ResolveInfo):
        user = info.context.user
        return user if user.is_authenticated else None

    # ---------------------------------------------------------
    def resolve_my_profile(self, info: ResolveInfo):
        user = info.context.user
        if not user.is_authenticated:
            return None
        return user.profile
