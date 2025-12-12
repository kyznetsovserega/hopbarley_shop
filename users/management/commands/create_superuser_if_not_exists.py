from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт суперпользователя, если он ещё не существует"

    def handle(self, *args: Any, **options: Any) -> None:
        username: str = "admin"
        email: str = "admin@example.com"
        password: str = "admin"

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS("✔ Superuser already exists"))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created (password: {password})"))
