from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from cart.utils import merge_session_cart_into_user_cart
from orders.models import Order
from reviews.models import Review

from .forms import ProfileUpdateForm, RegisterForm, UserUpdateForm

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

                return redirect("users:account")

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

            return redirect("users:account")
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
            return redirect("users:account")

        messages.error(request, "Пожалуйста, исправьте ошибки формы.")

    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    orders: QuerySet[Order] = Order.objects.filter(user=user).order_by("-created_at")

    reviewed_product_ids: set[int] = set(Review.objects.filter(user=user).values_list("product_id", flat=True))

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
    success_url = reverse_lazy("users:account")

    def form_valid(self, form: Any) -> HttpResponse:
        messages.success(self.request, "Пароль успешно изменён!")
        return super().form_valid(form)


# -------------------------
# PASSWORD RESET (Forgot password)
# -------------------------
class UserPasswordResetView(PasswordResetView):
    """
    Запрос восстановления пароля:
    - пользователь вводит email
    - отправляется письмо со ссылкой reset/<uid>/<token>/
    """

    template_name = "users/forgot_password.html"
    email_template_name = "users/emails/password_reset_email.txt"
    subject_template_name = "users/emails/password_reset_subject.txt"

    success_url = reverse_lazy("users:password_reset_done")

    def form_valid(self, form: Any) -> HttpResponse:
        # Одинаковое сообщение
        messages.info(self.request, "If this email exists, instructions will be sent.")
        return super().form_valid(form)


class UserPasswordResetDoneView(PasswordResetDoneView):
    """Шаг 2: страница 'проверьте почту'."""
    template_name = "users/password_reset_done.html"


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    """Шаг 3: установка нового пароля по ссылке из письма."""
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    """Шаг 4: пароль успешно изменён."""
    template_name = "users/password_reset_complete.html"
