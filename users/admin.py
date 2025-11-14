from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import UserProfile

class USerProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "Profile"

class CustomUserAdmin(UserAdmin):
    inlines = [USerProfileInline]


User = get_user_model()
admin.site.unregister(User)
admin.site.register(User,CustomUserAdmin)
