#!/bin/bash

# Script de despliegue simplificado para Alza API en Ubuntu VPS
# Ejecutar: bash deploy-simple.sh

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"; }
info() { echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO: $1${NC}"; }

# Banner
echo ""
echo "🚀 Alza API Deployment Script"
echo "================================"
echo ""

# Verificar requisitos
log "Verificando requisitos del sistema..."

if ! command -v docker &> /dev/null; then
    error "Docker no está instalado"
    echo "Instalar con: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose no está instalado"
    echo "Instalar con: sudo apt-get update && sudo apt-get install docker-compose-plugin"
    exit 1
fi

# Verificar archivos necesarios
if [ ! -f "docker-compose.yml" ]; then
    error "docker-compose.yml no encontrado"
    exit 1
fi

if [ ! -f "production.env" ]; then
    error "production.env no encontrado"
    exit 1
fi

log "✅ Requisitos verificados"

# Crear estructura de directorios
log "Creando estructura de directorios..."
mkdir -p logs/{api,django,nginx}
mkdir -p certbot/{conf,www}

# Configurar variables de entorno
log "Configurando variables de entorno..."
cp production.env .env

# Limpiar contenedores anteriores
log "Limpiando despliegue anterior..."
docker-compose down --remove-orphans --volumes 2>/dev/null || true
docker system prune -f 2>/dev/null || true

# Construir imágenes
log "Construyendo imágenes Docker..."
docker-compose build --no-cache --parallel

# Iniciar servicios
log "Iniciando servicios..."

# 1. Redis primero
info "Iniciando Redis..."
docker-compose up -d redis
sleep 5

# Verificar Redis
if ! docker-compose exec -T redis redis-cli ping &>/dev/null; then
    error "Redis no está funcionando"
    docker-compose logs redis
    exit 1
fi
log "✅ Redis funcionando"

# 2. API
info "Iniciando FastAPI..."
docker-compose up -d api
sleep 15

# Verificar API
for i in {1..6}; do
    if curl -f http://localhost:5544/health &>/dev/null; then
        log "✅ FastAPI funcionando"
        break
    else
        warn "Intento $i/6: API no responde, esperando..."
        sleep 10
    fi
    
    if [ $i -eq 6 ]; then
        error "API no responde después de 60 segundos"
        docker-compose logs api
        exit 1
    fi
done

# 3. Django
info "Iniciando Django..."
docker-compose up -d django-web
sleep 10

# Ejecutar migraciones y collectstatic
log "Ejecutando migraciones Django..."
docker-compose exec -T django-web python manage.py migrate --noinput || warn "Migraciones fallaron"

log "Recopilando archivos estáticos..."
docker-compose exec -T django-web python manage.py collectstatic --noinput || warn "Collectstatic falló"

# Verificar Django
for i in {1..6}; do
    if curl -f http://localhost:8880 &>/dev/null; then
        log "✅ Django funcionando"
        break
    else
        warn "Intento $i/6: Django no responde, esperando..."
        sleep 10
    fi
    
    if [ $i -eq 6 ]; then
        error "Django no responde después de 60 segundos"
        docker-compose logs django-web
        exit 1
    fi
done

# 4. Nginx
info "Iniciando Nginx..."
docker-compose up -d nginx
sleep 5

# Verificar Nginx
if curl -f http://localhost &>/dev/null; then
    log "✅ Nginx funcionando"
else
    warn "Nginx puede no estar funcionando correctamente"
fi

# Estado final
log "Verificando estado final..."
docker-compose ps

echo ""
log "🎉 Despliegue completado exitosamente!"
echo ""
info "🌐 Servicios disponibles:"
echo "  • API:          http://localhost:5544"
echo "  • API Health:   http://localhost:5544/health"
echo "  • API Docs:     http://localhost:5544/docs"
echo "  • Django:       http://localhost:8880"
echo "  • Nginx:        http://localhost"
echo ""
info "📋 Comandos útiles:"
echo "  • Ver logs API:     docker-compose logs -f api"
echo "  • Ver logs Django:  docker-compose logs -f django-web"
echo "  • Ver todos logs:   docker-compose logs -f"
echo "  • Reiniciar:        docker-compose restart"
echo "  • Detener:          docker-compose down"
echo "  • Estado:           docker-compose ps"
echo ""
info "🔧 Para SSL (opcional):"
echo "  • Ejecutar: ./init-letsencrypt.sh"
echo ""
log "✅ Despliegue finalizado"
