#!/bin/bash
set -e

echo "🚀 Iniciando Django Web Application..."

# Esperar a que la base de datos esté disponible
echo "⏳ Esperando conexión a la base de datos..."
python -c "
import time
import psycopg2
import os
from django.conf import settings

# Configurar Django
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alzaweb.settings')
django.setup()

# Intentar conectar a la base de datos
max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        from django.db import connection
        connection.ensure_connection()
        print('✅ Base de datos conectada')
        break
    except Exception as e:
        retry_count += 1
        print(f'⏳ Intento {retry_count}/{max_retries}: {e}')
        time.sleep(2)
else:
    print('❌ No se pudo conectar a la base de datos')
    exit(1)
"

# Ejecutar migraciones
echo "📦 Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "🎨 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Verificar que los archivos estáticos se generaron
echo "📋 Verificando archivos estáticos generados..."
ls -la /app/staticfiles/ || echo "⚠️  No se encontraron archivos estáticos"

# Crear superusuario si no existe (solo en desarrollo)
if [ "$DJANGO_DEBUG" = "True" ]; then
    echo "👤 Verificando superusuario..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@apgpacking.com', 'admin123')
    print('✅ Superusuario creado: admin/admin123')
else:
    print('✅ Superusuario ya existe')
"
fi

# Iniciar Gunicorn
echo "🚀 Iniciando Gunicorn..."
exec gunicorn --bind 0.0.0.0:8880 --workers 3 --timeout 120 alzaweb.wsgi:application
