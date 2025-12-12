# Hop & Barley Shop  
**Django / Django REST Framework / PostgreSQL / Docker**

Учебный проект — полноценный интернет-магазин, реализованный на **Django**  
с веб-интерфейсом (templates + session-based auth) и **REST API**  
на **Django REST Framework** с **JWT-авторизацией**.

Проект выполнен в соответствии с техническим заданием и демонстрирует
понимание Django, DRF, работы с базой данных, архитектуры, тестирования
и инфраструктуры.

---


## Стек технологий

- Python 3.12  
- Django 5.x  
- Django REST Framework (DRF)  
- JWT (access / refresh)  
- PostgreSQL  
- Docker & Docker Compose  
- Pytest + pytest-django + pytest-cov  
- Mypy (strict typing)  
- Flake8  
- Swagger / OpenAPI (drf-spectacular)

---

## Общие принципы (соответствие ТЗ)

- Веб-интерфейс использует **session-based authentication**.
- REST API использует **JWT**.
- PostgreSQL используется как основная БД.
- Проект полностью поднимается через **Docker Compose**.
- Архитектура разделена по приложениям и слоям ответственности.
- GraphQL реализован (отдельный endpoint `/graphql/`).

---

## Реализованная функциональность
<details> <summary><strong></strong></summary> <br>

### Каталог товаров (`/`, `/products/`)

- пагинация;
- поиск по названию и описанию;
- фильтрация по категории и диапазону цен;
- сортировка;
- иерархия категорий (parent / children).

### Страница товара (`/product/<slug>/`)

- детальная информация о товаре;
- изображения и характеристики;
- рейтинг и отзывы (1–5);
- добавление в корзину с выбором количества.

**Ограничения:**
- отзыв может оставить только авторизованный пользователь;
- отзыв возможен только после покупки;
- один пользователь — один отзыв на товар.

### Корзина (`/cart/`)

- session-based корзина для гостей и пользователей;
- добавление, удаление, изменение количества;
- автоматический пересчёт стоимости;
- проверка остатков на складе;
- объединение гостевой корзины с пользовательской после логина.

Бизнес-логика вынесена в сервисный слой: `cart/services.py`.

### Оформление заказа (`/checkout/`)

- форма оформления заказа с валидацией;
- поддержка guest и user заказов;
- транзакционное создание заказа;
- snapshot цен в `OrderItem`;
- эмуляция оплаты (fake payment);
- email-уведомления пользователю и администратору (console backend в dev).

### Личный кабинет (`/account/`)

- регистрация и вход (session auth);
- профиль пользователя (User + UserProfile);
- редактирование профиля;
- история заказов;
- смена пароля;
- автоматическое объединение корзин после входа.

Управление адресами доставки реализовано частично (опционально).

### Админ-панель (`/admin/`)

- управление товарами, категориями, заказами, отзывами;
- поиск и фильтры;
- кастомизация admin-интерфейса;
- базовая аналитика (агрегации и аннотации).

---

### REST API (`/api/`)

Реализованы:

- каталог товаров (list / retrieve);
- корзина (guest / auth);
- заказы (только свои);
- отзывы с бизнес-ограничениями;
- пользователи (регистрация, JWT login).

JWT:

- access / refresh токены;
- обновление токена;
- защита доступа к пользовательским данным.

---

### Swagger / OpenAPI

- Swagger UI: `/api/docs/`
- Schema: `/api/schema/`
- Авторизация через **Bearer Token**.

---

### GraphQL

- endpoint: `/graphql/`;
- реализован отдельно;
- не влияет на REST API;
- используется как бонусное улучшение;
- аналитические запросы реализованы частично.

</details>

---


## Быстрый старт (Docker)

### Клонирование проекта

```bash
git clone https://github.com/kyznetsovserega/hopbarley_shop.git
cd hopbarley_shop
git checkout dev
```

### Переменные окружения

Создать файл `.env` в корне проекта:

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=hopbarley
POSTGRES_USER=hopbarley
POSTGRES_PASSWORD=hopbarley
POSTGRES_HOST=db
POSTGRES_PORT=5432

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin12345
```


### Запуск проекта

```bash
docker compose up --build
```

Доступные адреса:
- http://localhost:8000/ — сайт  
- http://localhost:8000/admin/ — админ-панель  
- http://localhost:8000/api/docs/ — Swagger  
- http://localhost:8000/graphql/ — Graphql
- http://localhost:8000/api/redoc/ - Redoc

---

## Автоматические миграции и инициализация проекта

Проект настроен для запуска на чистой среде без ручных действий
со стороны пользователя.

При старте Docker-контейнера `web` автоматически выполняется
скрипт `entrypoint.sh`, который:

1. Применяет миграции базы данных:
   - `python manage.py makemigrations`
   - `python manage.py migrate`

2. Проверяет наличие данных в базе:
   - если в базе уже существуют продукты — загрузка данных пропускается;
   - если база пустая — загружаются **тестовые фикстуры**.

3. Загружает тестовые данные в базу:
   - товары: `products/fixtures/products.json`
   - пользователи и профили: `users/fixtures/test_database.json`
   - корзина: `cart/fixtures/cart_items_test.json`

   Данные используются для:
   - проверки функциональности проекта;
   - демонстрации работы каталога, корзины и заказов;
   - запуска автоматических тестов.

4. Создаёт суперпользователя (если отсутствует):
   - команда `create_superuser_if_not_exists`

5. Генерирует JWT-токен суперпользователя:
   - команда `print_jwt`
   - токен выводится в лог контейнера

6. Собирает статические файлы:
   - `python manage.py collectstatic --noinput`

7. Запускает приложение через Gunicorn.

Таким образом:
- база данных автоматически приводится в актуальное состояние;
- тестовые данные загружаются только при первом запуске;
- проект полностью готов к использованию сразу после `docker compose up`.


Просмотр токена:
```bash
docker compose logs web --tail=200 |
Select-String "ACCESS:","REFRESH:" |
Select-Object -Last 2
```

---


### Тестирование и качество кода

Запуск тестов
```bash
docker compose exec web pytest
```

С покрытием:
```bash
docker compose exec web pytest --cov=. --cov-report=term-missing
```

### Результаты тестирования

- Все тесты успешно пройдены (41 / 41);
- Общее покрытие кода: ~79%;
- Основной фокус тестирования: бизнес-логика, модели и REST API.

---

## Линтеры и типизация

```bash
docker compose exec web flake8
docker compose exec web mypy .
```
---

## CI / Code Quality

Настроен GitHub Actions CI:
- запуск тестов;
- flake8;
- mypy.

CI выполняется при каждом push и pull request.

## Example GraphQL query

<details>
<summary>Products with discount</summary>

```graphql
query {
  allProducts(discounted: true, orderBy: "-price", limit: 3) {
    name
    price
    discountPercent
    category {
      name
    }
    specifications {
      name
      value
    }
  }
}
```
</details> 

<details> <summary>Orders analytics</summary>

```graphql
query {
  totalRevenue
  ordersCount
  topProducts(limit: 3) {
    name
    price
  }
}
```
</details> 

<details> <summary>Product reviews</summary>

```graphql
query {
  productReviews(productSlug: "citra-hops") {
    rating
    comment
    username
    createdAt
  }
}
```

</details>

<details> <summary>Current user</summary>

```graphql
query {
  me {
    username
    email
    profile {
      phone
      fullAddress
    }
  }
}
```

</details>

<details> <summary>Update user</summary>

```graphql
mutation {
  updateUser(firstName: "John", lastName: "Doe") {
    ok
    error
    user {
      firstName
      lastName
      email
    }
  }
}
```
</details> 

<details> <summary>Cart</summary>

```graphql
query {
  cart {
    totalQuantity
    totalPrice
    items {
      quantity
      totalPrice
      product {
        name
        price
      }
    }
  }
}
```
</details> 

---

## Nginx

В проекте присутствует пример конфигурации `nginx.conf`,
подготовленный для возможного production-развёртывания.

В рамках учебного проекта и локальной разработки
приложение запускается напрямую через Gunicorn
без использования Nginx, что соответствует требованиям ТЗ.

---

## Структура проекта

<details> <summary><strong></strong></summary> <br>

```text
hopbarley_shop/
├── Dockerfile
├── docker-compose.yml
├──conftest.py
├──.pre-commit-config.yaml
├── entrypoint.sh
├── manage.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── pytest.ini
├── mypy.ini
├── Makefile
├── setup.cfg
├── nginx.conf ( задел для production)
│
├── main/                  # Конфигурация Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── products/              # Каталог товаров
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── filters.py
│   ├── signals.py
│   ├── fixtures/
│   └── tests/
│
├── cart/                  # Корзина и бизнес-логика
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   ├── fixtures/
│   └── tests/
│
├── orders/                # Заказы и оформление
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── forms.py
│   ├── email_services.py
│   ├── urls.py
│   └── tests/
│
├── reviews/               # Отзывы и рейтинги
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── tests/
│
├── users/                 # Пользователи и профили
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── signals.py
│   ├── urls.py
│   ├── management/
│   │   └── commands/
│   └── tests/
│
├── api/                   # REST API (DRF)
│   ├── serializers/
│   ├── views/
│   ├── urls.py
│   └── tests.py
│
├── graphql_api/            # GraphQL 
│   ├── schema.py
│   ├── queries/
│   ├── mutations/
│   └── types/
│
├── templates/              # Django templates
│   ├── base.html
│   ├── partials/
│   ├── products/
│   ├── cart/
│   ├── orders/
│   └── users/
│
└── static/                 # Статические файлы
    ├── css/
    ├── js/
    └── img/
```

</details> 



---

## Чек-лист соответствия ТЗ

- [X] Проект запускается через Docker Compose на чистой копии.
- [X] PostgreSQL используется.
- [X] Каталог: фильтры, поиск, пагинация.
- [X] Страница товара: детали, отзывы, добавление в корзину.
- [X] Корзина: управление, расчёт, проверка остатков.
- [X] Оформление заказа: создание, email-уведомления, валидация.
- [X] Личный кабинет: регистрация, вход, история заказов, редактирование профиля.
- [X] REST API: JWT-авторизация, документация, права доступа.
- [X] Админка: аналитика, фильтры, управление сущностями.
- [X] Swagger / OpenAPI работает (/api/docs/, /api/schema/, /redoc/).
- [X] Типизация и докстринги присутствуют.
- [X] Линтеры (flake8, mypy) без критичных ошибок.
- [X] Базовые тесты проходят (pytest, 41/41).
- [X] README полон и понятен.
- [X] Коммиты осмысленные, используется ветка dev.
- [X] Чек-лист приложен.

---
Ссылки

HTML шаблон:
https://github.com/MagicCodeGit/Hop-and-Barley.git

---

Репозиторий проекта (ветка dev):
https://github.com/kyznetsovserega/hopbarley_shop/tree/dev
