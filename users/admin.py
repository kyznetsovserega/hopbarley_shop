from __future__ import annotations

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import UserProfile


class UserProfileInline(admin.StackedInline):

    model = UserProfile
    can_delete = False
    verbose_name = "Профиль"
    verbose_name_plural = "Профили"
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


class CustomUserAdmin(UserAdmin):

    inlines = [UserProfileInline]


User = get_user_model()

# Перерегистрируем User с новой админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
