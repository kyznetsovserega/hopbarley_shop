from __future__ import annotations

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegisterForm(forms.ModelForm):
    """
    Форма регистрации пользователя:
    username + email + пароль.
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

    # --- VALIDATION ---

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким username уже существует.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")

        if p1 != p2:
            raise ValidationError("Пароли не совпадают.")
        return p2

    # --- SAVE ---

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # хэшим пароль

        if commit:
            user.save()
        return user
