from __future__ import annotations

import graphene
from django.core.exceptions import ValidationError
from graphene import ResolveInfo

from graphql_api.types.review_types import ReviewType
from orders.models import Order
from products.models import Product
from reviews.models import Review


class CreateReview(graphene.Mutation):
    """
    Создание отзыва на товар.
    """

    class Arguments:
        product_slug = graphene.String(required=True)
        rating = graphene.Int(required=True)
        comment = graphene.String(required=True)

    ok = graphene.Boolean()
    review = graphene.Field(ReviewType)
    error = graphene.String()

    # ---------------------------------------------------------
    def mutate(
        self,
        info: ResolveInfo,
        product_slug: str,
        rating: int,
        comment: str,
    ):
        user = info.context.user

        if not user.is_authenticated:
            return CreateReview(ok=False, error="Authentication required.")

        # ---- Product ----
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            return CreateReview(ok=False, error="Product not found.")

        # ---- Purchase check ----
        has_bought = Order.objects.filter(
            user=user,
            items__product=product,
            status__in=[Order.STATUS_PAID, Order.STATUS_DELIVERED],
        ).exists()

        if not has_bought:
            return CreateReview(
                ok=False,
                error="You can leave a review only after purchasing the product.",
            )

        # ---- One review per product ----
        if Review.objects.filter(user=user, product=product).exists():
            return CreateReview(
                ok=False,
                error="You have already reviewed this product.",
            )

        # ---- Create review ----
        try:
            review = Review.objects.create(
                user=user,
                product=product,
                rating=rating,
                comment=comment.strip(),
            )
            review.full_clean()
            review.save()
        except ValidationError as exc:
            return CreateReview(ok=False, error=str(exc))

        return CreateReview(ok=True, review=review)


class ReviewMutations(graphene.ObjectType):
    """
    Корневые мутации отзывов.
    """

    create_review = CreateReview.Field()
