#!/bin/bash

echo "🔧 Solucionando problema de archivos estáticos en Django Admin..."

# Detener contenedores
echo "📦 Deteniendo contenedores..."
docker-compose down

# Limpiar volúmenes de archivos estáticos
echo "🧹 Limpiando volúmenes de archivos estáticos..."
docker volume rm alza_api_django_static 2>/dev/null || echo "Volumen no existe, continuando..."

# Reconstruir solo el contenedor de Django
echo "🔨 Reconstruyendo contenedor de Django..."
docker-compose build --no-cache django-web

# Iniciar contenedores
echo "🚀 Iniciando contenedores..."
docker-compose up -d

# Esperar a que el contenedor esté listo
echo "⏳ Esperando a que Django esté listo..."
sleep 15

# Verificar logs del contenedor
echo "📋 Verificando logs de Django..."
docker logs alza_django --tail 20

# Verificar que los archivos estáticos se generaron
echo "📋 Verificando archivos estáticos..."
docker exec alza_django ls -la /app/staticfiles/ || echo "⚠️  No se pudieron verificar los archivos estáticos"

# Verificar que nginx puede acceder a los archivos
echo "📋 Verificando acceso de nginx a archivos estáticos..."
docker exec alza_nginx ls -la /var/www/static/ || echo "⚠️  Nginx no puede acceder a los archivos estáticos"

echo "✅ Proceso completado. Los archivos estáticos deberían estar funcionando ahora."
echo "🌐 Accede a: https://34.136.15.241/admin/"
echo "🔍 Si el problema persiste, revisa los logs con: docker logs alza_django"
