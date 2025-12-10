from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class Command(BaseCommand):
    help = "Автоматически выводит JWT токен администратора при запуске контейнера"

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username="admin")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Пользователь-администратор не найден"))
            return

        refresh = RefreshToken.for_user(user)

        self.stdout.write(self.style.SUCCESS("\n AUTO-GENERATED JWT TOKEN"))
        self.stdout.write(self.style.SUCCESS(f"ACCESS:  {refresh.access_token}"))
        self.stdout.write(self.style.SUCCESS(f"REFRESH: {refresh}"))
        self.stdout.write(self.style.SUCCESS("✔ Используйте этот токен в Swagger >> Авторизоваться"))
