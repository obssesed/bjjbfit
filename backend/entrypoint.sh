#!/bin/sh

# Esperar a que la base de datos esté lista (opcional si usamos healthcheck en compose)
echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 backend.wsgi:application
