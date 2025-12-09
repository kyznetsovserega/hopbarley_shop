from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):
    """
    Модель заказа.

    Хранит информацию о заказчике, статус заказа, способ оплаты,
    контактные данные и привязанные товары.
    """

    # ---- Статусы заказа ----
    STATUS_PENDING = "pending"
    STATUS_PENDING_PAYMENT = "pending_payment"
    STATUS_PAID = "paid"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает обработки"),
        (STATUS_PENDING_PAYMENT, "Ожидает оплаты"),
        (STATUS_PAID, "Оплачено"),
        (STATUS_SHIPPED, "Отправлено"),
        (STATUS_DELIVERED, "Доставлено"),
        (STATUS_CANCELLED, "Отменено"),
    ]

    # ---- Способы оплаты ----
    PAYMENT_CASH = "cash"
    PAYMENT_CARD = "card"

    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Наличными при получении"),
        (PAYMENT_CARD, "Банковская карта"),
    ]

    # ---- Основные поля заказа ----
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
        verbose_name='Пользователь',
        help_text="Пользователь, оформивший заказ (необязательно для гостей)."
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="Session Key",
        help_text="Session Key гостевого пользователя для привязки заказа."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Статус заказа',
        help_text="Текущий статус заказа."
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_CASH,
        verbose_name="Способ оплаты",
        help_text="Выбранный клиентом способ оплаты."
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Полная стоимость',
        help_text="Полная стоимость заказа (фиксируется при оформлении)."
    )

    shipping_address = models.TextField(
        verbose_name='Адрес доставки',
        null=True,
        blank=True,
        help_text="Адрес, по которому необходимо доставить заказ."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    # ---- Контактные данные ----
    full_name = models.CharField(
        max_length=255,
        verbose_name="ФИО",
        null=True,
        blank=True,
        help_text="ФИО клиента, оформившего заказ."
    )

    email = models.EmailField(
        verbose_name="Email",
        null=True,
        blank=True,
        help_text="Email клиента для уведомлений."
    )

    phone = models.CharField(
        max_length=32,
        verbose_name="Телефон",
        null=True,
        blank=True,
        help_text="Контактный телефон клиента."
    )

    comment = models.TextField(
        verbose_name="Комментарий",
        blank=True,
        null=True,
        help_text="Комментарий клиента к заказу."
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} ({self.get_status_display()})'

    @property
    def items_count(self) -> int:
        """
        Количество товарных позиций в заказе.
        """
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """
    Позиция товара внутри заказа.

    Хранит snapshot товара:
    цена и количество фиксируются в момент покупки.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ',
        help_text="Заказ, к которому относится данная товарная позиция."
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Товар',
        help_text="Товар, который был куплен."
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество',
        help_text="Количество единиц товара в заказе."
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена на момент покупки',
        help_text="Цена товара на момент оформления заказа (snapshot)."
    )

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    @property
    def total(self) -> float:
        """
        Полная стоимость конкретной позиции (цена x количество).
        """
        return self.quantity * self.price
