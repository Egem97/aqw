#!/bin/bash

echo "🚀 Despliegue Simplificado - Django sirve archivos estáticos directamente"
echo "====================================================================="

echo ""
echo "📋 Cambios realizados:"
echo "✅ Django configurado para servir archivos estáticos directamente"
echo "✅ Nginx ya no maneja archivos estáticos"
echo "✅ Volúmenes de archivos estáticos removidos"
echo "✅ Configuración simplificada"
echo ""

read -p "¿Continuar con el despliegue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Operación cancelada"
    exit 1
fi

echo ""
echo "🛑 Deteniendo contenedores..."
docker-compose down

echo ""
echo "🔨 Reconstruyendo contenedores..."
docker-compose build --no-cache

echo ""
echo "🚀 Iniciando servicios..."
docker-compose up -d

echo ""
echo "⏳ Esperando a que los servicios estén listos (30 segundos)..."
sleep 30

echo ""
echo "📋 Verificando estado de contenedores..."
docker-compose ps

echo ""
echo "📋 Verificando archivos estáticos en Django..."
docker exec alza_django ls -la /app/staticfiles/ 2>/dev/null || echo "⚠️  Error al verificar archivos estáticos"

echo ""
echo "📋 Logs recientes de Django..."
docker logs alza_django --tail 10

echo ""
echo "✅ Despliegue completado!"
echo ""
echo "🌐 Accede a tu aplicación:"
echo "   - Panel Admin: https://34.136.15.241/admin/"
echo "   - API Docs: https://34.136.15.241/docs"
echo ""
echo "🔍 Si hay problemas, revisa los logs:"
echo "   - Django: docker logs alza_django"
echo "   - Nginx: docker logs alza_nginx"
echo "   - API: docker logs alza_api"
