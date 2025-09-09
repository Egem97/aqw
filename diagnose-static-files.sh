#!/bin/bash

echo "🔍 Diagnóstico de archivos estáticos Django"
echo "=========================================="

echo ""
echo "📋 Estado de contenedores:"
docker-compose ps

echo ""
echo "📋 Volúmenes Docker:"
docker volume ls | grep alza

echo ""
echo "📋 Archivos estáticos en Django:"
if docker exec alza_django ls -la /app/staticfiles/ 2>/dev/null; then
    echo "✅ Archivos estáticos encontrados en Django"
else
    echo "❌ No se encontraron archivos estáticos en Django"
fi

echo ""
echo "📋 Archivos estáticos en Nginx:"
if docker exec alza_nginx ls -la /var/www/static/ 2>/dev/null; then
    echo "✅ Archivos estáticos encontrados en Nginx"
else
    echo "❌ No se encontraron archivos estáticos en Nginx"
fi

echo ""
echo "📋 Logs recientes de Django:"
docker logs alza_django --tail 15

echo ""
echo "📋 Configuración de Django (STATIC_ROOT):"
docker exec alza_django python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alzaweb.settings')
django.setup()
from django.conf import settings
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'STATICFILES_DIRS: {settings.STATICFILES_DIRS}')
"

echo ""
echo "📋 Test de acceso a archivos estáticos:"
echo "   Probando acceso a CSS de admin..."
if curl -s -I https://34.136.15.241/static/admin/css/base.css | head -1; then
    echo "✅ CSS de admin accesible"
else
    echo "❌ CSS de admin no accesible"
fi
