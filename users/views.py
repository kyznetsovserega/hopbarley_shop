from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from orders.models import Order

@login_required
def account_view(request):

    if request.method == "POST":
        # update profile
        user = request.user
        full_name = request.POST.get("full_name", "")
        email = request.POST.get("email", "")

        # split full_name → first/last
        parts = full_name.strip().split(" ", 1)
        user.first_name = parts[0]
        if len(parts) > 1:
            user.last_name = parts[1]

        user.email = email
        user.save()

        return redirect("users:account")

    # GET
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "users/account.html", {
        "orders": orders,
    })


from django.shortcuts import render, redirect
from django.contrib import messages

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Пока просто сообщение
        messages.info(request, "If this email exists, instructions will be sent.")
        return redirect("users:login")

    return render(request, "users/forgot_password.html")

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        # ищем пользователя по email
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = None

        if username:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("users:account")

        messages.error(request, "Incorrect email or password.")

    return render(request, "users/login.html", {
        "form": {},   # чтобы template мог показывать form.errors
    })

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import RegisterForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("users:account")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})
