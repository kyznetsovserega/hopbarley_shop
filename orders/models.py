from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает оплаты"),
        (STATUS_PAID, "Оплачено"),
        (STATUS_SHIPPED, "Отправлено"),
        (STATUS_DELIVERED, "Доставлено"),
        (STATUS_CANCELLED, "Отменено"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
        verbose_name='Пользователь',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Статус заказа',
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Полная стоимость',
    )
    shipping_address = models.TextField(
        verbose_name='Адрес доставки',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    full_name = models.CharField(
        max_length=255,
        verbose_name="ФИО",
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name="Email",
        null=True,
        blank=True,
    )
    phone = models.CharField(
        max_length=32,
        verbose_name="Телефон",
        null=True,
        blank=True,
    )
    comment = models.TextField(
        verbose_name="Комментарий",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} ({self.get_status_display()})'


    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Товар',
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Цена товара на момент оформления заказа (snapshot)",
        verbose_name='Цена на момент покупки',
    )

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    @property
    def total(self):
        return self.quantity * self.price
