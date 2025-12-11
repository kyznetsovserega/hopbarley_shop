from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # LOGIN / LOGOUT / REGISTER
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    # FORGOT PASSWORD (placeholder)
    path("forgot/", views.forgot_password_view, name="forgot_password"),
    # ACCOUNT PROFILE PAGE
    path("account/", views.account_view, name="account"),
    # PASSWORD CHANGE
    path(
        "account/password-change/",
        views.UserPasswordChangeView.as_view(),
        name="password_change",
    ),
]
