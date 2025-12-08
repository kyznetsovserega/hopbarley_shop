from __future__ import annotations

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from products.models import Product


class Review(models.Model):
    """
    Отзыв пользователя на товар.
    Один пользователь может оставить только один отзыв на один продукт.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        related_query_name="review",
        verbose_name="Товар",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        related_query_name="review",
        verbose_name="Пользователь",
    )

    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Оценка",
    )

    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_review"
            )
        ]

    def clean(self):
        """
        Рейтинг должен быть 1–5.
        """
        if not (1 <= self.rating <= 5):
            raise ValidationError("Рейтинг должен быть от 1 до 5.")

    def __str__(self):
        username = self.user.username or self.user.email
        return f"{username} → {self.product.name} ({self.rating}/5)"
