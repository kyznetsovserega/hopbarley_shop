from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from products.models import Product
from orders.models import Order
from .forms import ReviewForm
from .models import Review


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # 1. Проверка: пользователь должен сначала купить товар
    has_bought = (
        Order.objects
        .filter(
            user=request.user,
            items__product=product,
            status__in=["paid", "delivered"]  # статусы "успешного" заказа
        )
        .exists()
    )

    if not has_bought:
        messages.error(
            request,
            "Вы можете оставить отзыв только после покупки этого товара."
        )
        return redirect("products:product_detail", slug=product.slug)

    # 2. Проверка: только один отзыв на товар от одного пользователя
    if Review.objects.filter(user=request.user, product=product).exists():
        messages.error(request, "Вы уже оставили отзыв для этого товара.")
        return redirect("products:product_detail", slug=product.slug)

    # 3. Обработка формы
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Спасибо! Ваш отзыв сохранён.")
        else:
            messages.error(request, "Исправьте ошибки в форме перед отправкой.")

    return redirect("products:product_detail", slug=product.slug)
