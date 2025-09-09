#!/bin/bash

echo "🔧 Script de reparación de archivos estáticos Django"
echo "=================================================="

echo ""
echo "📋 Pasos a ejecutar:"
echo "1. Detener contenedores"
echo "2. Limpiar volúmenes"
echo "3. Reconstruir Django"
echo "4. Iniciar servicios"
echo "5. Verificar archivos estáticos"
echo ""

read -p "¿Continuar? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Operación cancelada"
    exit 1
fi

echo ""
echo "🛑 Paso 1: Deteniendo contenedores..."
docker-compose down

echo ""
echo "🧹 Paso 2: Limpiando volúmenes de archivos estáticos..."
docker volume rm alza_api_django_static 2>/dev/null || echo "   ℹ️  Volumen no existe, continuando..."

echo ""
echo "🔨 Paso 3: Reconstruyendo contenedor de Django..."
docker-compose build --no-cache django-web

echo ""
echo "🚀 Paso 4: Iniciando contenedores..."
docker-compose up -d

echo ""
echo "⏳ Esperando a que Django esté listo (30 segundos)..."
sleep 30

echo ""
echo "📋 Paso 5: Verificando archivos estáticos..."
echo "   📁 Archivos en Django:"
docker exec alza_django ls -la /app/staticfiles/ 2>/dev/null || echo "   ❌ Error al acceder a archivos estáticos en Django"

echo ""
echo "   📁 Archivos en Nginx:"
docker exec alza_nginx ls -la /var/www/static/ 2>/dev/null || echo "   ❌ Error al acceder a archivos estáticos en Nginx"

echo ""
echo "📋 Logs recientes de Django:"
docker logs alza_django --tail 10

echo ""
echo "✅ Proceso completado!"
echo "🌐 Accede a: https://34.136.15.241/admin/"
echo ""
echo "🔍 Si el problema persiste:"
echo "   - Revisa logs: docker logs alza_django"
echo "   - Verifica nginx: docker logs alza_nginx"
echo "   - Comprueba volúmenes: docker volume ls"
