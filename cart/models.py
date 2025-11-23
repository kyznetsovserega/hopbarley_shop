from django.db import models

from django.contrib.auth import get_user_model
from django.db.models import CASCADE

from products.models import Product

User = get_user_model()

class CartItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart_items',
    )

    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'session_key','product')

    def __str__(self):
        return f"{self.product.title} * {self.quantity}"