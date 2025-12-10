from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт суперпользователя, если он ещё не существует"

    def handle(self, *args, **options):
        username = "admin"
        email = "admin@example.com"
        password = "admin"

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS("✔ Superuser already exists"))
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(
                f"Superuser '{username}' created (password: {password})"
            ))
