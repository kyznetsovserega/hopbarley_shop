from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from cart.models import CartItem

from .forms import CheckoutForm
from .models import Order
from .services import create_order_from_cart
from .email_services import send_order_confirmation, notify_admin

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as UserType
else:
    UserType = Any


# ======================================================================
# CHECKOUT VIEW
# ======================================================================
def checkout_view(request: HttpRequest) -> HttpResponse:
    """
    Основная страница оформления заказа.
    Если выбран метод 'card' → перенаправляем на fake-payment.
    """

    # --- 1. Session key ---
    if not request.session.session_key:
        request.session.create()
    session_key: str = request.session.session_key  # type: ignore[assignment]

    # --- 2. Корзина ---
    if request.user.is_authenticated:
        cart_items: QuerySet[CartItem] = CartItem.objects.filter(user=request.user).select_related("product")
    else:
        cart_items = CartItem.objects.filter(session_key=session_key).select_related("product")

    cart_total = sum(item.total_price for item in cart_items)

    # ==================================================================
    # GET
    # ==================================================================
    if request.method == "GET":
        initial_data: Dict[str, Any] = {}

        user: UserType = request.user

        if request.user.is_authenticated:
            profile = getattr(user, "profile", None)

            initial_data = {
                "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                "email": user.email,
                "phone": profile.phone if profile else "",
                "shipping_address": profile.address if profile else "",
            }

        form = CheckoutForm(initial=initial_data)

        return render(
            request,
            "orders/checkout.html",
            {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
            },
        )

    # ==================================================================
    # POST
    # ==================================================================
    form = CheckoutForm(request.POST)

    # Корзина пуста
    if not cart_items.exists():
        return render(
            request,
            "orders/checkout.html",
            {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": "Корзина пуста",
            },
        )

    # Невалидные данные формы
    if not form.is_valid():
        return render(
            request,
            "orders/checkout.html",
            {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
            },
        )

    # Создание заказа
    try:
        order = create_order_from_cart(request, form.cleaned_data)

        payment_method: str | None = form.cleaned_data.get("payment_method")

        # --- Если карта → имитация оплаты
        if payment_method == "card":
            return redirect("orders:fake_payment", order_id=order.id)

        # Защита от повторной отправки писем (двойной клик/повторный POST)
        if not order.emails_sent:
            send_order_confirmation(order)
            notify_admin(order)
            order.emails_sent = True
            order.save(update_fields=["emails_sent"])

        # --- Обычная success-страница
        return redirect("orders:success", order_id=order.id)

    except ValidationError as e:
        return render(
            request,
            "orders/checkout.html",
            {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": str(e),
            },
        )

    except Exception:
        return render(
            request,
            "orders/checkout.html",
            {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": "Ошибка оформления заказа. Попробуйте позднее.",
            },
        )


# ======================================================================
# FAKE PAYMENT PAGE
# ======================================================================
def fake_payment_view(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    После псевдо-оплаты:
     это просто страница имитации оплаты.
    Здесь НЕ меняем статус и НЕ отправляем письма - избегаем дубли/paid раньше времени.
    """

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Order not found")

    return render(request, "orders/fake_payment.html", {"order_id": order.id})


# ======================================================================
# FAKE PAYMENT SUCCESS
# ======================================================================
def fake_payment_success(request: HttpRequest, order_id: int) -> HttpResponseRedirect:
    """
    После псевдо-оплаты:
    - статус заказа становится paid
    - отправляется email клиенту и админу
    - перевод на success
    """

    try:
        order = Order.objects.get(id=order_id)
        # статус paid (точка "успешной оплаты")
        if order.status != Order.STATUS_PAID:
            order.status = Order.STATUS_PAID
            order.save(update_fields=["status"])
        # защита от повторной отправки писем
        if not order.emails_sent:
            send_order_confirmation(order)
            notify_admin(order)
            order.emails_sent = True
            order.save(update_fields=["emails_sent"])

    except Order.DoesNotExist:
        raise Http404("Order not found")

    return redirect("orders:success", order_id=order_id)


# ======================================================================
# SUCCESS PAGE
# ======================================================================
def order_success_view(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    Страница успешного заказа.
    """
    return render(request, "orders/success.html", {"order_id": order_id})
