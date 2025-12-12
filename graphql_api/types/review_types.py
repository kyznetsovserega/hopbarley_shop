from __future__ import annotations

import graphene
from graphene_django import DjangoObjectType

from reviews.models import Review


class ReviewType(DjangoObjectType):
    """
    GraphQL тип отзыва на товар.
    """

    username = graphene.String(
        description="Username or email of the review author."
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "rating",
            "comment",
            "created_at",
            "user",
            "product",
        )
        description = "Product review."

    def resolve_username(self, info) -> str:
        user = self.user
        return user.username or user.email
