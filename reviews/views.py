from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from products.views import ProductDetailView

from products.models import Product
from orders.models import Order
from .forms import ReviewForm
from .models import Review


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Покупка
    has_bought = Order.objects.filter(
        user=request.user,
        items__product=product,
        status__in=["paid", "delivered"]
    ).exists()

    if not has_bought:
        messages.error(request, "Можно оставить отзыв только после покупки.")
        return redirect("products:product_detail", slug=slug)

    # Один отзыв
    if Review.objects.filter(user=request.user, product=product).exists():
        messages.error(request, "Вы уже оставили отзыв.")
        return redirect("products:product_detail", slug=slug)

    # POST
    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Спасибо! Ваш отзыв опубликован.")
            return redirect("products:product_detail", slug=slug)

        # Ошибочная форма > показываем CBV с invalid_form
        view = ProductDetailView.as_view(
            extra_context={"invalid_form": form}
        )
        return view(request, slug=slug)

    return redirect("products:product_detail", slug=slug)
