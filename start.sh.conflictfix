#!/bin/bash
<<<<<<< HEAD


echo "=== ѕроверка переменных окружени€ ==="
echo "DJANGO_SUPERUSER_USERNAME: $DJANGO_SUPERUSER_USERNAME"
echo "DJANGO_SUPERUSER_EMAIL: $DJANGO_SUPERUSER_EMAIL"
echo "DJANGO_SUPERUSER_PASSWORD: [скрыто]"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..."
echo "======================================"

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_superuser_if_none
=======
python manage.py migrate --noinput
python manage.py collectstatic --noinput
>>>>>>> 9aea3ddadb5000e1052f30a5add167a0c33219e9
gunicorn crime_komi.wsgi
