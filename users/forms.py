from __future__ import annotations

from typing import Any, Dict

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

from .models import UserProfile


# =========================================================
# REGISTER FORM
# =========================================================

class RegisterForm(forms.ModelForm):
    """
    Форма регистрации пользователя: username + email + password.
    """

    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Введите пароль"}),
        strip=False,
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Повторите пароль"}),
        strip=False,
    )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Введите имя пользователя"}),
            "email": forms.EmailInput(attrs={"placeholder": "Введите email"}),
        }

    # -------------------
    # VALIDATION METHODS
    # -------------------

    def clean_username(self) -> str:
        username: str = (self.cleaned_data.get("username") or "").strip()

        if not username:
            raise ValidationError("Введите имя пользователя.")

        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким username уже существует.")

        return username

    def clean_email(self) -> str:
        email: str = (self.cleaned_data.get("email") or "").strip().lower()

        if not email:
            raise ValidationError("Введите email.")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")

        return email

    def clean(self) -> Dict[str, Any]:
        cleaned_data: Dict[str, Any] = super().clean()
        p1: str | None = cleaned_data.get("password1")
        p2: str | None = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise ValidationError({"password2": "Пароли не совпадают."})

        if p1:
            try:
                validate_password(p1)
            except ValidationError as e:
                raise ValidationError({"password1": e.messages})

        return cleaned_data

    # -------------------
    # SAVE
    # -------------------

    def save(self, commit: bool = True) -> User:
        user: User = super().save(commit=False)

        password: str = self.cleaned_data["password1"]
        user.set_password(password)

        if commit:
            user.save()

        return user


# =========================================================
# USER UPDATE FORM
# =========================================================

class UserUpdateForm(forms.ModelForm):
    """
    Обновление данных встроенной модели User:
    first_name, last_name, email.
    """

    first_name = forms.CharField(
        required=False,
        label="Имя",
        widget=forms.TextInput(attrs={"placeholder": "Имя"}),
    )

    last_name = forms.CharField(
        required=False,
        label="Фамилия",
        widget=forms.TextInput(attrs={"placeholder": "Фамилия"}),
    )

    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def clean_email(self) -> str:
        email: str = (self.cleaned_data.get("email") or "").strip().lower()
        user_id: int | None = self.instance.id

        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise ValidationError("Этот email уже используется другим пользователем.")

        return email


# =========================================================
# PROFILE UPDATE FORM
# =========================================================

class ProfileUpdateForm(forms.ModelForm):
    """
    Обновление профиля пользователя:
    телефон, город, адрес, дата рождения.
    """

    phone = forms.CharField(
        required=False,
        label="Телефон",
        validators=[
            RegexValidator(
                regex=r"^[0-9+\-() ]*$",
                message="Телефон может содержать только цифры и символы + - ( )",
            )
        ],
        widget=forms.TextInput(attrs={"placeholder": "Телефон"}),
    )

    city = forms.CharField(
        required=False,
        label="Город",
        widget=forms.TextInput(attrs={"placeholder": "Город"}),
    )

    address = forms.CharField(
        required=False,
        label="Адрес",
        widget=forms.Textarea(attrs={"placeholder": "Адрес", "rows": 3}),
    )

    date_of_birth = forms.DateField(
        required=False,
        label="Дата рождения",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = UserProfile
        fields = ("phone", "city", "address", "date_of_birth")
