#!/bin/bash

# Script para desplegar localmente (sin VPS)
# Ejecutar: bash deploy-local.sh

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[LOCAL] $1${NC}"; }
warn() { echo -e "${YELLOW}[LOCAL] WARNING: $1${NC}"; }
error() { echo -e "${RED}[LOCAL] ERROR: $1${NC}"; }
info() { echo -e "${BLUE}[LOCAL] INFO: $1${NC}"; }

echo ""
echo "🏠 Despliegue Local - Alza API"
echo "=============================="
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose no está instalado"
    exit 1
fi

# Limpiar proyecto
log "Limpiando proyecto..."
bash cleanup.sh

# Crear directorios
log "Creando directorios..."
mkdir -p logs/{api,django,nginx}
mkdir -p certbot/{conf,www}

# Configurar entorno
log "Configurando entorno..."
cp production.env .env

# Detener servicios anteriores
log "Deteniendo servicios anteriores..."
docker-compose down --remove-orphans || true

# Construir imágenes
log "Construyendo imágenes..."
docker-compose build --no-cache

# Iniciar servicios
log "Iniciando servicios..."

# 1. Redis
info "Iniciando Redis..."
docker-compose up -d redis
sleep 5

# 2. API
info "Iniciando FastAPI..."
docker-compose up -d api
sleep 15

# 3. Django
info "Iniciando Django..."
docker-compose up -d django-web
sleep 10

# Migraciones
log "Ejecutando migraciones Django..."
docker-compose exec -T django-web python manage.py migrate --noinput || warn "Migraciones fallaron"

log "Recopilando archivos estáticos..."
docker-compose exec -T django-web python manage.py collectstatic --noinput || warn "Collectstatic falló"

# 4. Nginx
info "Iniciando Nginx..."
docker-compose up -d nginx
sleep 5

# Verificar servicios
log "Verificando servicios..."
docker-compose ps

echo ""
log "🎉 Despliegue local completado!"
echo ""
info "🌐 URLs disponibles:"
echo "  • API:          http://localhost:5544"
echo "  • API Health:   http://localhost:5544/health"
echo "  • API Docs:     http://localhost:5544/docs"
echo "  • Django:       http://localhost:8880"
echo "  • Nginx:        http://localhost"
echo ""
info "📋 Comandos útiles:"
echo "  • Ver logs:     docker-compose logs -f"
echo "  • Detener:      docker-compose down"
echo "  • Estado:       docker-compose ps"
echo ""
log "✅ Despliegue local finalizado"
