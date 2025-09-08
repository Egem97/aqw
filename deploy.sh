#!/bin/bash

# Script de despliegue para FastAPI + Django en VPS
# Ejecutar en el VPS: bash deploy.sh

set -e

echo "🚀 Iniciando despliegue de Alza API + Django Web..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    error "docker-compose.yml no encontrado. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado. Instálalo primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose no está instalado. Instálalo primero."
    exit 1
fi

# Crear directorios necesarios
log "Creando directorios necesarios..."
mkdir -p logs/nginx
mkdir -p logs/django
mkdir -p logs/api
mkdir -p certbot/conf
mkdir -p certbot/www

# Detener servicios existentes si están corriendo
log "Deteniendo servicios existentes..."
docker-compose down --remove-orphans || true

# Construir imágenes
log "Construyendo imágenes..."
log "  - Construyendo FastAPI..."
docker-compose build --no-cache api

log "  - Construyendo Django..."
docker-compose build --no-cache django-web

# Iniciar servicios de base de datos primero
log "Iniciando servicios de cache..."
docker-compose up -d redis

# Esperar a que Redis esté listo
log "Esperando a que Redis esté listo..."
sleep 10

# Verificar que Redis responde
for i in {1..10}; do
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        log "✅ Redis está funcionando"
        break
    else
        warn "Intento $i/10: Redis no responde aún, esperando..."
        sleep 5
    fi
    
    if [ $i -eq 10 ]; then
        error "Redis no responde después de 10 intentos"
        docker-compose logs redis
        exit 1
    fi
done

# Nota: PostgreSQL es externo, no verificamos conexión aquí
log "ℹ️  Usando PostgreSQL externo en 34.136.15.241:5666"

# Iniciar API
log "Iniciando FastAPI..."
docker-compose up -d api

# Esperar a que la API esté lista
log "Esperando a que FastAPI esté lista..."
sleep 30

# Verificar que la API responde
for i in {1..10}; do
    if docker-compose exec -T api curl -f http://localhost:5544/health > /dev/null 2>&1; then
        log "✅ FastAPI está respondiendo correctamente"
        break
    else
        warn "Intento $i/10: FastAPI no responde aún, esperando..."
        sleep 10
    fi
    
    if [ $i -eq 10 ]; then
        error "FastAPI no responde después de 10 intentos"
        docker-compose logs api
        exit 1
    fi
done

# Ejecutar migraciones de Django
log "Ejecutando migraciones de Django..."
docker-compose run --rm django-web python manage.py migrate --noinput

# Recopilar archivos estáticos de Django
log "Recopilando archivos estáticos de Django..."
docker-compose run --rm django-web python manage.py collectstatic --noinput

# Crear superusuario de Django (opcional)
log "Creando superusuario de Django (si no existe)..."
docker-compose run --rm django-web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
EOF

# Iniciar Django
log "Iniciando Django Web..."
docker-compose up -d django-web

# Esperar a que Django esté listo
log "Esperando a que Django esté listo..."
sleep 20

# Verificar que Django responde
for i in {1..10}; do
    if docker-compose exec -T django-web curl -f http://localhost:8880 > /dev/null 2>&1; then
        log "✅ Django está respondiendo correctamente"
        break
    else
        warn "Intento $i/10: Django no responde aún, esperando..."
        sleep 10
    fi
    
    if [ $i -eq 10 ]; then
        error "Django no responde después de 10 intentos"
        docker-compose logs django-web
        exit 1
    fi
done

# Configurar SSL si es la primera vez
if [ ! -f "certbot/conf/live/34.136.15.241/fullchain.pem" ]; then
    log "Configurando SSL por primera vez..."
    
    # Hacer el script ejecutable
    chmod +x init-letsencrypt.sh
    
    # Ejecutar inicialización de SSL
    ./init-letsencrypt.sh
else
    log "Certificados SSL ya existen, iniciando Nginx..."
    docker-compose up -d nginx
fi

# Iniciar todos los servicios
log "Iniciando todos los servicios..."
docker-compose up -d

# Verificar estado final
log "Verificando estado final de los servicios..."
sleep 15

# Verificar servicios
services=("redis" "api" "django-web" "nginx")
for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        log "✅ $service está funcionando"
    else
        error "❌ $service no está funcionando"
        docker-compose logs $service
    fi
done

# Mostrar información final
log "🎉 Despliegue completado!"
echo ""
log "📊 Estado de los servicios:"
docker-compose ps

echo ""
log "🌐 URLs disponibles:"
echo "  • Django Web: https://34.136.15.241/"
echo "  • FastAPI:    https://34.136.15.241/api/"
echo "  • API Docs:   https://34.136.15.241/docs"
echo "  • Django Admin: https://34.136.15.241/admin/"

echo ""
log "👤 Credenciales Django Admin:"
echo "  • Usuario: admin"
echo "  • Contraseña: admin123"
echo "  • Cambiar contraseña después del primer login"

echo ""
log "📋 Comandos útiles:"
echo "  • Ver logs: docker-compose logs -f [servicio]"
echo "  • Reiniciar: docker-compose restart [servicio]"
echo "  • Detener: docker-compose down"
echo "  • Estado: docker-compose ps"

echo ""
log "🔐 SSL:"
if [ -f "certbot/conf/live/34.136.15.241/fullchain.pem" ]; then
    echo "  ✅ Certificados SSL configurados"
    echo "  • Renovación automática cada 12 horas"
else
    echo "  ⚠️  Certificados SSL no configurados"
    echo "  • Ejecuta: ./init-letsencrypt.sh"
fi

echo ""
log "🏗️ Arquitectura desplegada:"
echo "  • Nginx (Gateway + SSL)"
echo "  • Django Web (Frontend/Admin)"
echo "  • FastAPI (API REST)"
echo "  • PostgreSQL (Externo - 34.136.15.241:5666)"
echo "  • Redis (Cache compartido)"