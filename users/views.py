from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.db.models import QuerySet
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy

from cart.utils import merge_session_cart_into_user_cart
from orders.models import Order
from reviews.models import Review

from .forms import ProfileUpdateForm
from .forms import RegisterForm
from .forms import UserUpdateForm

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as UserType
else:
    UserType = Any


# -------------------------
# LOGIN
# -------------------------
def login_view(request: HttpRequest) -> HttpResponse:
    """
    Логин по email + password.
    После успешного входа объединяет гостевую корзину с корзиной пользователя.
    """

    if request.method == "POST":
        email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        username: str | None = None

        from django.contrib.auth.models import User  # runtime import OK

        try:
            user_obj: User = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            pass

        if username:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                merge_session_cart_into_user_cart(user, request.session.session_key)

                return redirect("account")

        messages.error(request, "Incorrect email or password.")

    return render(request, "users/login.html")


# -------------------------
# REGISTRATION
# -------------------------
def register_view(request: HttpRequest) -> HttpResponse:
    """
    Регистрация нового пользователя.
    После создания аккаунта — login + объединение корзины.
    """

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user: UserType = form.save()
            login(request, user)

            merge_session_cart_into_user_cart(user, request.session.session_key)

            return redirect("account")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


# -------------------------
# LOGOUT
# -------------------------
def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    logout(request)
    return redirect("products:product_list")


# -------------------------
# ACCOUNT (PROFILE + ORDERS)
# -------------------------
@login_required
def account_view(request: HttpRequest) -> HttpResponse:
    """
    Личный кабинет пользователя:
    - просмотр профиля
    - редактирование User + Profile
    - история заказов
    """

    user: UserType = request.user  # type: ignore[assignment]
    profile = user.profile  # profile всегда есть по сигналу

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "Профиль успешно обновлён!")
            return redirect("account")

        messages.error(request, "Пожалуйста, исправьте ошибки формы.")

    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    orders: QuerySet[Order] = Order.objects.filter(user=user).order_by("-created_at")

    reviewed_product_ids: set[int] = set(
        Review.objects.filter(user=user).values_list("product_id", flat=True)
    )

    return render(
        request,
        "users/account.html",
        {
            "orders": orders,
            "profile": profile,
            "user_form": user_form,
            "profile_form": profile_form,
            "reviewed_product_ids": reviewed_product_ids,
        },
    )


# -------------------------
# PASSWORD CHANGE
# -------------------------
class UserPasswordChangeView(PasswordChangeView):
    """
    Смена пароля через встроенную CBV.
    """

    template_name = "users/change_password.html"
    success_url = reverse_lazy("account")

    def form_valid(self, form: Any) -> HttpResponse:
        messages.success(self.request, "Пароль успешно изменён!")
        return super().form_valid(form)


# -------------------------
# FORGOT PASSWORD (PLACEHOLDER)
# -------------------------
def forgot_password_view(request: HttpRequest) -> HttpResponse:
    """
    Демонстрационная заглушка.
    """

    if request.method == "POST":
        messages.info(request, "If this email exists, instructions will be sent.")
        return redirect("users:login")

    return render(request, "users/forgot_password.html")
