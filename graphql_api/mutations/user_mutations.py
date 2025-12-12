from __future__ import annotations

from datetime import date
from typing import Optional

import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from graphene import ResolveInfo

from graphql_api.types.user_types import UserProfileType, UserType
from users.models import UserProfile

User = get_user_model()


# ======================================================================
# UPDATE PROFILE
# ======================================================================
class UpdateProfile(graphene.Mutation):
    """
    Обновление профиля пользователя.

    Обновляемые поля:
    - phone
    - city
    - address
    - date_of_birth
    """

    class Arguments:
        phone = graphene.String(required=False)
        city = graphene.String(required=False)
        address = graphene.String(required=False)
        date_of_birth = graphene.Date(required=False)

    ok = graphene.Boolean()
    profile = graphene.Field(UserProfileType)
    error = graphene.String()

    # ---------------------------------------------------------
    def mutate(
        self,
        info: ResolveInfo,
        phone: Optional[str] = None,
        city: Optional[str] = None,
        address: Optional[str] = None,
        date_of_birth: Optional[date] = None,
    ) -> UpdateProfile:
        user = info.context.user

        if not user.is_authenticated:
            return UpdateProfile(ok=False, error="Authentication required.")

        profile: UserProfile = user.profile

        if phone is not None:
            profile.phone = phone
        if city is not None:
            profile.city = city
        if address is not None:
            profile.address = address
        if date_of_birth is not None:
            profile.date_of_birth = date_of_birth

        try:
            profile.full_clean()
            profile.save()
        except ValidationError as exc:
            return UpdateProfile(ok=False, error=str(exc))

        return UpdateProfile(ok=True, profile=profile)


# ======================================================================
# UPDATE USER
# ======================================================================
class UpdateUser(graphene.Mutation):
    """
    Обновление данных пользователя.

    Обновляемые поля:
    - first_name
    - last_name
    - email
    """

    class Arguments:
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)
        email = graphene.String(required=False)

    ok = graphene.Boolean()
    user = graphene.Field(UserType)
    error = graphene.String()

    # ---------------------------------------------------------
    def mutate(
        self,
        info: ResolveInfo,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> UpdateUser:
        user = info.context.user

        if not user.is_authenticated:
            return UpdateUser(ok=False, error="Authentication required.")

        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if email is not None:
            user.email = email.strip().lower()

        try:
            user.full_clean()
            user.save()
        except ValidationError as exc:
            return UpdateUser(ok=False, error=str(exc))

        return UpdateUser(ok=True, user=user)


# ======================================================================
# ROOT MUTATIONS
# ======================================================================
class UserMutations(graphene.ObjectType):
    """
    Корневые мутации пользователя.
    """

    update_profile = UpdateProfile.Field()
    update_user = UpdateUser.Field()
