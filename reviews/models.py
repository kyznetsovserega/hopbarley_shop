from django.db import models

from django.conf import settings
from products.models import Product

class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Товар',
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь',
    )

    rating = models.IntegerField(
        choices= [(i, i) for i in range(1, 6)],
        verbose_name='Оценка',
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = [ '-created_at']

    def __str__(self):
        return f'{self.user.username} -> {self.product.name} ({self.rating}/5)'

