from __future__ import annotations

from typing import Any

import pytest
from django.core import mail
from django.urls import reverse

from orders.models import Order


@pytest.mark.django_db
def test_fake_payment_success_sends_emails_once(client_web: Any, order_fixture: Any) -> None:
    """
    1) Первый вызов fake_payment_success -> отправляет 2 письма (клиент + админ)
    2) Повторный вызов -> писем не добавляет (emails_sent=True)
    """

    order: Order = order_fixture
    order.email = "customer@test.com"
    order.full_name = "Test Customer"
    order.phone = "123"
    order.shipping_address = "Test address"
    order.payment_method = Order.PAYMENT_CARD  # имитируем оплату картой-сценарий
    order.save()

    url = reverse("orders:fake_payment_success", kwargs={"order_id": order.id})

    # 1) первый вызов
    resp1 = client_web.get(url)
    assert resp1.status_code == 302
    assert len(mail.outbox) == 2

    # Проверяем, что флаг выставился
    order.refresh_from_db()
    assert order.emails_sent is True

    # 2) повторный вызов
    resp2 = client_web.get(url)
    assert resp2.status_code == 302
    assert len(mail.outbox) == 2  # дублей нет
