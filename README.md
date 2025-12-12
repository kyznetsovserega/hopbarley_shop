### Автогенерация суперпользователя и JWT токена при запуске Docker

Этот проект поддерживает автоматическую подготовку окружения при первом запуске Docker:

- создаётся суперпользователь (если он ещё не существует);
- генерируется JWT-токен суперюзера;
- токен автоматически выводится в консоль;
- Swagger автоматически получает возможность авторизации через Bearer Token;
- это избавляет от ручного создания админа и получения токена во время проверки проекта.

**Management-команды проекта:**

- `users/management/commands/create_superuser_if_not_exists.py`
- `users/management/commands/print_jwt.py`

Эти команды автоматически выполняются внутри Docker при запуске контейнера `web`.


-------------------------------------------------------------------------------------------

# HopBarley Shop API

![CI](https://github.com/kyznetsovserega/hopbarley_shop/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-82%25-yellow)
![Mypy](https://img.shields.io/badge/mypy-strict-blue)
![Flake8](https://img.shields.io/badge/flake8-passing-brightgreen)
# Trigger
