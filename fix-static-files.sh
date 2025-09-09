#!/bin/bash

echo "🔧 Solucionando problema de archivos estáticos en Django Admin..."

# Detener contenedores
echo "📦 Deteniendo contenedores..."
docker-compose down

# Reconstruir solo el contenedor de Django
echo "🔨 Reconstruyendo contenedor de Django..."
docker-compose build --no-cache django-web

# Iniciar contenedores
echo "🚀 Iniciando contenedores..."
docker-compose up -d

# Verificar que los archivos estáticos se generaron
echo "📋 Verificando archivos estáticos..."
sleep 10
docker exec alza_django ls -la /app/staticfiles/

echo "✅ Proceso completado. Los archivos estáticos deberían estar funcionando ahora."
echo "🌐 Accede a: https://34.136.15.241/admin/"
