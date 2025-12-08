from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from orders.models import Order
from .forms import RegisterForm

from cart.utils import merge_session_cart_into_user_cart


# ACCOUNT VIEW
@login_required
def account_view(request):
    """
    Личный кабинет пользователя.
    Позволяет редактировать данные профиля и смотреть историю заказов.
    """
    user = request.user
    profile = user.profile  # создаётся сигналами автоматически

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        city = request.POST.get("city", "").strip()
        address = request.POST.get("address", "").strip()
        dob = request.POST.get("date_of_birth", None)

        # ---- Update User ----
        parts = full_name.split(" ", 1)
        user.first_name = parts[0] if parts else ""
        user.last_name = parts[1] if len(parts) > 1 else ""
        user.email = email
        user.save()

        # ---- Update Profile ----
        profile.phone = phone
        profile.city = city
        profile.address = address
        if dob:
            profile.date_of_birth = dob
        profile.save()

        messages.success(request, "Профиль успешно обновлён!")
        return redirect("account")  # <---- ВАЖНО: фикс для всех тестов!!!

    orders = Order.objects.filter(user=user).order_by("-created_at")

    return render(request, "users/account.html", {
        "orders": orders,
        "profile": profile,
    })


# FORGOT PASSWORD
def forgot_password_view(request):
    """
    Заглушка восстановления пароля.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        messages.info(request, "If this email exists, instructions will be sent.")
        return redirect("users:login")

    return render(request, "users/forgot_password.html")


# LOGIN VIEW (EMAIL > USERNAME)
def login_view(request):
    """
    Авторизация пользователя по email + password.
    После успешного входа корзина гостя объединяется с корзиной пользователя.
    """
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        # получаем username по email
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = None

        if username:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

                # переносим корзину гостя > корзину пользователя
                merge_session_cart_into_user_cart(
                    user, request.session.session_key
                )

                return redirect("account")

        messages.error(request, "Incorrect email or password.")

    return render(request, "users/login.html", {
        "form": {},
    })


# REGISTER
def register_view(request):
    """
    Регистрация нового пользователя.
    После создания учётной записи — объединение корзины гостя и пользователя.
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            # merge при регистрации
            merge_session_cart_into_user_cart(
                user, request.session.session_key
            )

            return redirect("account")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect("products:list")
