from __future__ import annotations

from typing import Iterable

import graphene
from graphene import ResolveInfo

from reviews.models import Review
from graphql_api.types.review_types import ReviewType


class ReviewQuery(graphene.ObjectType):
    """
    GraphQL-запросы отзывов.
    """

    product_reviews = graphene.List(
        ReviewType,
        product_slug=graphene.String(required=True),
        description="Returns all reviews for a product.",
    )

    my_reviews = graphene.List(
        ReviewType,
        description="Returns reviews created by the current user.",
    )

    # ---------------------------------------------------------
    def resolve_product_reviews(
        self,
        info: ResolveInfo,
        product_slug: str,
    ) -> Iterable[Review]:
        return (
            Review.objects.select_related("user", "product").filter(product__slug=product_slug).order_by("-created_at")
        )

    # ---------------------------------------------------------
    def resolve_my_reviews(self, info: ResolveInfo) -> Iterable[Review]:
        user = info.context.user
        if not user.is_authenticated:
            return Review.objects.none()

        return Review.objects.select_related("product").filter(user=user).order_by("-created_at")
