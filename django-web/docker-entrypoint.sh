#!/bin/bash
set -e

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe (solo en desarrollo)
if [ "$DJANGO_DEBUG" = "True" ]; then
    echo "Verificando superusuario..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@apgpacking.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"
fi

# Iniciar Gunicorn
echo "Iniciando Gunicorn..."
exec gunicorn --bind 0.0.0.0:8880 --workers 3 alzaweb.wsgi:application
