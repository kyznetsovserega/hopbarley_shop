from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import pytest
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse


def _url_or_path(url: str) -> str:
    """
    В письме обычно абсолютный URL (http://testserver/...).
    """
    parsed = urlparse(url)
    return parsed.path if parsed.scheme else url


def _get_reset_request_url() -> str:
    """
    Пытаемся использовать reverse по имени.
    """
    try:
        return reverse("users:forgot_password")
    except Exception:
        return "/users/forgot/"


def _extract_first_reset_link(email_body: str) -> str:
    """
    Достаём первую ссылку на /users/reset/... из тела письма.
    """
    match = re.search(r"(https?://[^\s]+)?(/users/reset/[^\s]+/)", email_body)
    if not match:
        match = re.search(r"(https?://[^\s]+/users/reset/[^\s]+/)", email_body)
    assert match, f"Не нашли ссылку reset в письме. Тело письма:\n{email_body}"

    if match.group(2):
        domain = match.group(1) or ""
        return f"{domain}{match.group(2)}"
    return match.group(1)


@pytest.mark.django_db
def test_password_reset_happy_path(client: Any) -> None:
    """
    1) POST на /users/forgot/ с email существующего юзера -> редирект на done
    2) В outbox появляется письмо
    3) В письме есть ссылка /users/reset/<uidb64>/<token>/
    4) GET по ссылке -> редирект на /users/reset/<uidb64>/set-password/
    5) POST нового пароля -> редирект на /users/reset/done/
    6) Пароль реально изменился
    """
    user = User.objects.create_user(
        username="john",
        email="john@example.com",
        password="OldPass12345",
    )

    reset_request_url = _get_reset_request_url()

    # шаг 1: запросить сброс
    resp = client.post(reset_request_url, {"email": "john@example.com"})
    assert resp.status_code in (302, 303)

    # шаг 2: проверяем письмо
    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert "john@example.com" in message.to

    body = message.body or ""
    reset_link = _extract_first_reset_link(body)
    reset_path = _url_or_path(reset_link)

    # шаг 3-4: открыть reset ссылку
    resp2 = client.get(reset_path)
    # В логах 302 -> /users/reset/<uid>/set-password/
    assert resp2.status_code in (200, 302, 303)

    # Если сразу редирект — идём дальше по Location
    if resp2.status_code in (302, 303):
        set_password_path = resp2["Location"]
    else:
        # Если страница подтверждения токена отрисовывается, то форма POST'ится туда же.
        # Используем текущий path.
        set_password_path = reset_path

    # шаг 5: задать новый пароль
    new_password = "NewStrongPass12345"
    resp3 = client.post(
        set_password_path,
        {"new_password1": new_password, "new_password2": new_password},
    )

    # в логах финал 302 на /users/reset/done/
    assert resp3.status_code in (302, 303)

    # шаг 6: пароль реально обновился
    user.refresh_from_db()
    assert user.check_password(new_password) is True


@pytest.mark.django_db
def test_password_reset_unknown_email_does_not_send_email(client: Any) -> None:
    """
    На неизвестный email ответ должен быть таким же,
    но письмо отправляться не должно.
    """
    reset_request_url = _get_reset_request_url()

    resp = client.post(reset_request_url, {"email": "nobody@example.com"})
    assert resp.status_code in (302, 303)

    # Никаких писем
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_password_reset_requires_matching_passwords(client: Any) -> None:
    """
    Негативный сценарий: разные пароли -> остаёмся на форме и видим ошибки.
    """
    user = User.objects.create_user(
        username="kate",
        email="kate@example.com",
        password="OldPass12345",
    )

    reset_request_url = _get_reset_request_url()
    client.post(reset_request_url, {"email": "kate@example.com"})
    assert len(mail.outbox) == 1

    reset_link = _extract_first_reset_link(mail.outbox[0].body or "")
    reset_path = _url_or_path(reset_link)

    resp2 = client.get(reset_path)
    if resp2.status_code in (302, 303):
        set_password_path = resp2["Location"]
    else:
        set_password_path = reset_path

    resp3 = client.post(
        set_password_path,
        {"new_password1": "NewPass111", "new_password2": "NewPass222"},
    )

    # Пароль не должен измениться.
    assert resp3.status_code in (200, 302, 303)

    user.refresh_from_db()
    assert user.check_password("OldPass12345") is True
    assert user.check_password("NewPass111") is False
