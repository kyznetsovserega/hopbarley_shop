from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError

from cart.models import CartItem
from .forms import CheckoutForm
from .services import create_order_from_cart


def checkout_view(request):
    # гарантия, что сессия существует
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # корзина для текущей сессии
    cart_items = CartItem.objects.filter(session_key=session_key)
    cart_total = sum(item.get_total_price() for item in cart_items)

    form = CheckoutForm(request.POST or None)

    # --- POST ---
    if request.method == "POST":

        # форма невалидна
        if not form.is_valid():
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
            })

        # пустая корзина
        if not cart_items.exists():
            error = "Корзина пуста"
            messages.error(request, error)
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": error,
            })

        # создание заказа
        try:
            order = create_order_from_cart(request, form.cleaned_data)
            return redirect("orders:success", order_id=order.id)

        except ValidationError as e:
            error = str(e)
            messages.error(request, error)
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": error,
            })

    # --- GET ---
    return render(request, "orders/checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "cart_total": cart_total,
    })


def order_success_view(request, order_id):
    return render(request, "orders/success.html", {"order_id": order_id})
