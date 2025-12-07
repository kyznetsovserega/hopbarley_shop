"""
Модуль представлений для модуля Orders.

Реализует:
- страницу оформления заказа (checkout)
- страницу успешного оформления заказа.

Основная задача валидировать данные, проверить корзину
и передать управление сервису create_order_from_cart().
"""

from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError

from cart.models import CartItem
from .forms import CheckoutForm
from .services import create_order_from_cart


# ======================================================================
# CHECKOUT VIEW
# ======================================================================
def checkout_view(request):
    """
    Основная страница оформления заказа.

    Логика:
    1. Обеспечивает наличие session_key (для гостей).
    2. Загружает корзину по session_key.
    3. Обрабатывает GET — отображает форму.
    4. Обрабатывает POST:
        - проверяет, что корзина не пуста
        - валидирует форму
        - вызывает сервис создания заказа
        - при успехе делает redirect на страницу успеха.
    """

    # ------------------------------------------------------------------
    # 1. Session Key — обязателен для незарегистрированных пользователей
    # ------------------------------------------------------------------
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # ------------------------------------------------------------------
    # 2. Корзина
    # ------------------------------------------------------------------
    #    - если пользователь авторизован → user-cart
    #    - если гость → session-cart
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user).select_related("product")
    else:
        cart_items = CartItem.objects.filter(session_key=session_key).select_related("product")

    cart_total = sum(item.total_price for item in cart_items)

    # ------------------------------------------------------------------
    # 3. Форма
    # ------------------------------------------------------------------
    form = CheckoutForm(request.POST or None)

    # ------------------------------------------------------------------
    # 4. POST — оформление заказа
    # ------------------------------------------------------------------
    if request.method == "POST":

        # ---- 4.1 Корзина пуста ----
        if not cart_items.exists():
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": "Корзина пуста",
            })

        # ---- 4.2 Ошибка формы ----
        if not form.is_valid():
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
            })

        # ---- 4.3 Создание заказа ----
        try:
            order = create_order_from_cart(request, form.cleaned_data)
            return redirect("orders:success", order_id=order.id)

        except ValidationError as e:
            # Бизнес-ошибки: например, недостаточно товара
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": str(e),
            })

        except Exception:
            # Технические сбои
            return render(request, "orders/checkout.html", {
                "form": form,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "error": "Ошибка оформления заказа. Попробуйте позднее.",
            })

    # ------------------------------------------------------------------
    # 5. GET — просто отображаем страницу
    # ------------------------------------------------------------------
    return render(request, "orders/checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "cart_total": cart_total,
    })


# ======================================================================
# SUCCESS PAGE
# ======================================================================
def order_success_view(request, order_id):
    """
    Страница успешного оформления заказа.
    Показывает пользователю номер созданного заказа.
    """
    return render(request, "orders/success.html", {"order_id": order_id})
