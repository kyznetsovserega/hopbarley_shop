from django.core.mail import send_mail
from django.conf import settings


def send_order_confirmation(order):
    """
    Письмо покупателю о том, что заказ успешно оформлен.
    """

    # Если email не указан — просто ничего не делаем
    if not order.email:
        return

    subject = f"Ваш заказ #{order.id} успешно оформлен"
    message = (
        f"Здравствуйте, {order.full_name}!\n\n"
        f"Ваш заказ #{order.id} принят в обработку.\n"
        f"Сумма заказа: {order.total_price} ₽\n\n"
        f"Адрес доставки:\n{order.shipping_address}\n\n"
        f"Спасибо за покупку в Hop & Barley!"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )


def notify_admin(order):
    """
    Уведомление администратору о новом заказе.
    """

    admin_email = getattr(settings, "ADMIN_EMAIL", None)
    if not admin_email:
        return

    subject = f"Новый заказ #{order.id}"
    message = (
        f"Поступил новый заказ #{order.id}\n\n"
        f"Сумма: {order.total_price} ₽\n"
        f"Покупатель: {order.full_name} ({order.email}, {order.phone})\n"
        f"Адрес доставки:\n{order.shipping_address}\n\n"
        f"Комментарий: {order.comment}"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email],
        fail_silently=False,
    )
