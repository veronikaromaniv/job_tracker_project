web: python manage.py migrate --noinput && python manage.py createsuperuser --noinput || true && python manage.py collectstatic --noinput && gunicorn config.wsgi --log-file -
