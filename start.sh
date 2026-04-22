#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_superuser_if_none
gunicorn crime_komi.wsgi
