from __future__ import annotations

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Инлайн для профиля пользователя.
    """

    model = UserProfile
    can_delete = False
    verbose_name = "Профиль"
    verbose_name_plural = "Профиль"
    fk_name = "user"

    fields = (
        "phone",
        "city",
        "address",
        "date_of_birth",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")

    extra = 0


class CustomUserAdmin(UserAdmin):
    """
    Доработанная админка Django User:
    — показывает профиль
    — добавляет поля профиля в список
    """

    inlines = [UserProfileInline]

    # Добавляем отображение профиля в списке пользователей
    list_display = UserAdmin.list_display + (
        "get_phone",
        "get_city",
    )

    search_fields = UserAdmin.search_fields + ("profile__phone", "profile__city")

    def get_phone(self, obj):
        return obj.profile.phone
    get_phone.short_description = "Телефон"

    def get_city(self, obj):
        return obj.profile.city
    get_city.short_description = "Город"


User = get_user_model()

# Перерегистрируем User с новой админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
