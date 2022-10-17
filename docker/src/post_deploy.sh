#! /bin/sh

set -e
set -u
set -x

# Wait for DB
dockerize -wait tcp://postgres:"${POSTGRES_INTERNAL_PORT}" -timeout 30s

umask 000 # setting broad permissions to share log volume

# Migrate models
python3 manage.py migrate --no-input

# Collect static files to serve them with nginx
python3 manage.py collectstatic --no-input

# Create the superuser for the platform
python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model();User.objects.filter(username='${SUPERUSER_NAME}').exists() or User.objects.create_superuser('${SUPERUSER_NAME}', '${SUPERUSER_MAIL}', '${SUPERUSER_PASSWORD}')"

# Set the number of Django threads to use
num_threads=${DJANGO_THREADS}

# Start the gunicorn server
/usr/local/bin/gunicorn backend.wsgi:application --workers "${num_threads}" --bind :"${BACKEND_PORT}" --timeout "$CONF_GUNICORN_TIMEOUT" "$CONF_GUNICORN_EXTRA_ARGS"
