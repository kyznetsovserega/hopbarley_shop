from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # LOGIN / LOGOUT / REGISTER
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # PASSWORD RESET (real email flow)
    path("forgot/", views.UserPasswordResetView.as_view(), name="forgot_password"),
    path("forgot/done/", views.UserPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", views.UserPasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # ACCOUNT PROFILE PAGE
    path("account/", views.account_view, name="account"),

    # PASSWORD CHANGE (logged-in)
    path(
        "account/password-change/",
        views.UserPasswordChangeView.as_view(),
        name="password_change",
    ),
]
