"""
Web-представления корзины.

Используют CartService — единый слой бизнес-логики, который управляет
корзиной как для гостей (session_key), так и для авторизованных пользователей.

Данный модуль отвечает ТОЛЬКО за:
- обработку HTTP-запросов
- валидацию форм (AddToCartForm)
- вывод шаблонов

Вся бизнес-логика находится в cart/services.py.
"""

from __future__ import annotations

from typing import Any, Dict

from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from products.models import Product
from .forms import AddToCartForm
from .services import CartService


# ======================================================================
# ADD TO CART
# ======================================================================
@require_POST
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponseRedirect:
    """
    Добавление товара в корзину через веб-форму.
    """
    product = get_object_or_404(Product, id=product_id)

    form = AddToCartForm(
        data=request.POST,
        product=product,
        request=request,
    )

    if form.is_valid():
        quantity = form.cleaned_data["quantity"]

        try:
            CartService(request).add(product, quantity)
            messages.success(request, "Товар добавлен в корзину.")
        except Exception as e:
            messages.error(request, str(e))

    else:
        messages.error(request, "Некорректное количество.")

    return redirect("cart:detail")


# ======================================================================
# REMOVE ITEM
# ======================================================================
def remove_from_cart(request: HttpRequest, item_id: int) -> HttpResponseRedirect:
    """
    Удаление элемента корзины.
    """
    service = CartService(request)
    try:
        service.remove(item_id)
        messages.success(request, "Товар удалён.")
    except Exception:
        messages.error(request, "Не удалось удалить товар.")

    return redirect("cart:detail")


# ======================================================================
# INCREASE QUANTITY
# ======================================================================
def increase_quantity(request: HttpRequest, item_id: int) -> HttpResponseRedirect:
    """
    Увеличивает количество товара на 1.
    Проверки stock выполняет CartService.
    """
    service = CartService(request)

    try:
        service.increase(item_id)
    except Exception as e:
        messages.error(request, str(e))

    return redirect("cart:detail")


# ======================================================================
# DECREASE QUANTITY
# ======================================================================
def decrease_quantity(request: HttpRequest, item_id: int) -> HttpResponseRedirect:
    """
    Уменьшает количество товара.
    Если товар становится 1 > уменьшается до 0 и удаляется.
    """
    service = CartService(request)

    try:
        service.decrease(item_id)
    except Exception as e:
        messages.error(request, str(e))

    return redirect("cart:detail")


# ======================================================================
# CLEAR CART
# ======================================================================
def clear_cart(request: HttpRequest) -> HttpResponseRedirect:
    """
    Полностью очищает корзину текущего владельца (user или session_key).
    """
    CartService(request).clear()
    messages.info(request, "Корзина очищена.")
    return redirect("cart:detail")


# ======================================================================
# CART DETAIL PAGE
# ======================================================================
def cart_detail(request: HttpRequest) -> HttpResponse:
    """
    Страница корзины: список товаров + итоговая сумма.
    """
    service = CartService(request)
    items = service.get_items()
    total = service.get_total()

    context: Dict[str, Any] = {
        "items": items,
        "total": total,
    }

    return render(request, "cart/cart_detail.html", context)
