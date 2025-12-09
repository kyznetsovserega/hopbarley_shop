"""
Модуль представлений для оформления заказа.
Поддерживает:
- обычное оформление
- фейковую оплату картой
"""


from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.http import Http404

from cart.models import CartItem
from .forms import CheckoutForm
from .services import create_order_from_cart
from .models import Order


# ======================================================================
# CHECKOUT VIEW
# ======================================================================
def checkout_view(request):
    """
    Основная страница оформления заказа.
    Если выбран метод 'card' > перенаправляем на fake-payment.
    """

    # --- 1. Session key ---
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # --- 2. Корзина ---
    if request.user.is_authenticated:
        cart_items = (
            CartItem.objects.filter(user=request.user).select_related("product")
        )
    else:
        cart_items = (
            CartItem.objects.filter(session_key=session_key).select_related("product")
        )

    cart_total = sum(item.total_price for item in cart_items)

    # --- 3. GET: автозаполнение формы ---
    if request.method == "GET":
        initial_data = {}

        if request.user.is_authenticated:
            user = request.user
            profile = getattr(user, "profile", None)

            initial_data = {
                "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                "email": user.email,
                "phone": profile.phone if profile else "",
                "shipping_address": profile.address if profile else "",
            }

        form = CheckoutForm(initial=initial_data)

    # --- 4. POST ---
    else:
        form = CheckoutForm(request.POST)

        # Корзина пуста
        if not cart_items.exists():
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": "Корзина пуста",
            })

        # Форма невалидна
        if not form.is_valid():
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
            })

        # Создание заказа
        try:
            order = create_order_from_cart(request, form.cleaned_data)

            payment_method = form.cleaned_data.get("payment_method")

            # --- Если карта > фейковая оплата ---
            if payment_method == "card":
                return redirect("orders:fake_payment", order_id=order.id)

            # --- Иначе обычный success ---
            return redirect("orders:success", order_id=order.id)

        except ValidationError as e:
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": str(e),
            })

        except Exception:
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": "Ошибка оформления заказа. Попробуйте позднее.",
            })

    # --- GET: отображение ---
    return render(request, "orders/checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "cart_total": cart_total,
    })


# ======================================================================
# FAKE PAYMENT PAGE
# ======================================================================
def fake_payment_view(request, order_id):
    """
    Имитация страницы оплаты. Пользователь нажимает кнопку "Оплатить".
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Order not found")

    return render(request, "orders/fake_payment.html", {"order_id": order_id})


# ======================================================================
# FAKE PAYMENT SUCCESS
# ======================================================================
def fake_payment_success(request, order_id):
    """
    После псевдо-оплаты:
    - статус заказа становится paid
    - перевод на success страницу
    """
    try:
        order = Order.objects.get(id=order_id)
        order.status = Order.STATUS_PAID
        order.save()
    except Order.DoesNotExist:
        raise Http404("Order not found")

    return redirect("orders:success", order_id=order_id)


# ======================================================================
# SUCCESS PAGE
# ======================================================================
def order_success_view(request, order_id):
    """
    Страница успешного заказа.
    """
    return render(request, "orders/success.html", {"order_id": order_id})
