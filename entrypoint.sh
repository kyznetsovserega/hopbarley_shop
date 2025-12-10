#!/bin/sh

echo "Running entrypoint..."

python manage.py makemigrations
python manage.py migrate

echo "Checking if fixtures need to be loaded..."

python manage.py shell -c "
from products.models import Product
import sys
if Product.objects.exists():
    sys.exit(0)
sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo 'Fixtures already present — skipping.'
else
    echo 'Loading initial fixtures...'
    python manage.py loaddata products/fixtures/products.json
    python manage.py loaddata users/fixtures/test_database.json
    python manage.py loaddata cart/fixtures/cart_items_test.json
    echo 'Fixtures loaded.'
fi

echo "Ensuring superuser exists..."
python manage.py create_superuser_if_not_exists
python manage.py print_jwt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
gunicorn main.wsgi:application --bind 0.0.0.0:8000
