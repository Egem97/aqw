#!/bin/bash

echo "🔍 Diagnóstico Simplificado - Django sirve archivos estáticos"
echo "=========================================================="

echo ""
echo "📋 Estado de contenedores:"
docker-compose ps

echo ""
echo "📋 Archivos estáticos en Django:"
if docker exec alza_django ls -la /app/staticfiles/ 2>/dev/null; then
    echo "✅ Archivos estáticos encontrados en Django"
    echo ""
    echo "📁 Contenido del directorio admin:"
    docker exec alza_django ls -la /app/staticfiles/admin/ 2>/dev/null || echo "⚠️  No se encontró directorio admin"
else
    echo "❌ No se encontraron archivos estáticos en Django"
fi

echo ""
echo "📋 Configuración de Django:"
docker exec alza_django python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alzaweb.settings')
django.setup()
from django.conf import settings
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'DEBUG: {settings.DEBUG}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
"

echo ""
echo "📋 Test de acceso directo a archivos estáticos:"
echo "   Probando CSS de admin desde Django..."
if docker exec alza_django curl -s -I http://localhost:8880/static/admin/css/base.css | head -1; then
    echo "✅ CSS de admin accesible desde Django"
else
    echo "❌ CSS de admin no accesible desde Django"
fi

echo ""
echo "📋 Test de acceso externo:"
echo "   Probando CSS de admin desde nginx..."
if curl -s -I https://34.136.15.241/static/admin/css/base.css | head -1; then
    echo "✅ CSS de admin accesible externamente"
else
    echo "❌ CSS de admin no accesible externamente"
fi

echo ""
echo "📋 Logs recientes de Django:"
docker logs alza_django --tail 10

echo ""
echo "📋 Logs recientes de Nginx:"
docker logs alza_nginx --tail 5
