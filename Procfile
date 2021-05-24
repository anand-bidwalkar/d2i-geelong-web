release: python manage.py migrate --no-input
release: python manage.py loaddata dump.json
web: gunicorn Property_Portal.wsgi --log-file -