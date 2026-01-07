#!/bin/sh
set -e

echo "Running entrypoint..."

# -------------------------------------------------------------------
# Дожидаемся Postgres (только если указан POSTGRES_HOST)
# -------------------------------------------------------------------
if [ -n "${POSTGRES_HOST:-}" ]; then
  echo "Waiting for Postgres at ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
  until python - <<'PY'
import os, sys
import psycopg2

host = os.getenv("POSTGRES_HOST", "db")
port = int(os.getenv("POSTGRES_PORT", "5432"))
db   = os.getenv("POSTGRES_DB", "hopbarley")
user = os.getenv("POSTGRES_USER", "hopbarley")
pwd  = os.getenv("POSTGRES_PASSWORD", "hopbarley")

try:
    psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pwd).close()
except Exception:
    sys.exit(1)
sys.exit(0)
PY
  do
    sleep 1
  done
fi

# -------------------------------------------------------------------
# Django
# -------------------------------------------------------------------
python manage.py migrate
python manage.py collectstatic --noinput

# -------------------------------------------------------------------
# Подготовка MEDIA для картинок товаров
# -------------------------------------------------------------------
echo "Preparing media files for demo..."
mkdir -p /app/media/products
cp -n /app/static/img/products/*.jpg /app/media/products/ 2>/dev/null || true

# -------------------------------------------------------------------
# Загрузка fixtures только при явном запросе
# -------------------------------------------------------------------
if [ "${LOAD_FIXTURES:-0}" = "1" ]; then
  echo "LOAD_FIXTURES=1 -> checking if products exist..."

  if python manage.py shell -c "from products.models import Product; import sys; sys.exit(0 if Product.objects.exists() else 1)"; then
    echo "Fixtures already present — skipping."
  else
    echo "Loading initial fixtures..."
    python manage.py loaddata products/fixtures/products.json
    python manage.py loaddata users/fixtures/test_database.json
    python manage.py loaddata cart/fixtures/cart_items_test.json
    echo "Fixtures loaded."
  fi

  echo "Ensuring superuser exists..."
  python manage.py create_superuser_if_not_exists

  echo "Printing JWT..."
  python manage.py print_jwt
fi

# -------------------------------------------------------------------
# Запускаем команду из docker-compose
# -------------------------------------------------------------------
echo "Entrypoint done. Starting: $*"
exec "$@"
