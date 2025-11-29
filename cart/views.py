from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product
from .models import CartItem
from .forms import AddToCartForm


def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = AddToCartForm(request.POST)

    if form.is_valid():
        quantity = form.cleaned_data["quantity"]
        session_key = _get_session_key(request)

        item, created = CartItem.objects.get_or_create(
            session_key=session_key,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            item.quantity += quantity
            item.save()

    return redirect("cart:detail")


def remove_from_cart(request, item_id):
    session_key = _get_session_key(request)
    CartItem.objects.filter(id=item_id, session_key=session_key).delete()
    return redirect("cart:detail")

def increase_quantity(request, item_id):
    session_key = _get_session_key(request)
    item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
    item.quantity += 1
    item.save()
    return redirect("cart:detail")

def decrease_quantity(request, item_id):
    session_key = _get_session_key(request)
    item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect("cart:detail")

def clear_cart(request):
    session_key = _get_session_key(request)
    CartItem.objects.filter(session_key=session_key).delete()
    return redirect("cart:detail")

def cart_detail(request):
    session_key = _get_session_key(request)
    items = CartItem.objects.filter(session_key=session_key)

    total = sum(item.get_total_price() for item in items)

    return render(request, "cart/cart_detail.html", {
        "items": items,
        "total": total,
    })
