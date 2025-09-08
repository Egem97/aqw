#!/bin/bash

# Script para subir el proyecto al VPS y desplegarlo
# Ejecutar desde tu máquina local: bash upload-to-vps.sh

VPS_IP="34.136.15.241"
VPS_USER="root"  # Cambia por tu usuario
VPS_PATH="/opt/alza-api"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] $1${NC}"
}

log "🚀 Subiendo proyecto al VPS $VPS_IP..."

# Verificar conexión SSH
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $VPS_USER@$VPS_IP exit 2>/dev/null; then
    error "No se puede conectar al VPS. Verifica:"
    echo "  1. Que el VPS esté encendido"
    echo "  2. Que tengas acceso SSH configurado"
    echo "  3. Que la IP sea correcta: $VPS_IP"
    exit 1
fi

# Crear directorio en el VPS
log "Creando directorio en el VPS..."
ssh $VPS_USER@$VPS_IP "mkdir -p $VPS_PATH"

# Subir archivos (excluyendo archivos innecesarios)
log "Subiendo archivos al VPS..."
rsync -avz --progress \
    --exclude='env/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.git/' \
    --exclude='logs/' \
    --exclude='certbot/' \
    --exclude='*.log' \
    ./ $VPS_USER@$VPS_IP:$VPS_PATH/

# Hacer ejecutables los scripts
log "Configurando permisos..."
ssh $VPS_USER@$VPS_IP "cd $VPS_PATH && chmod +x *.sh"

# Copiar configuración de producción
log "Configurando variables de entorno..."
ssh $VPS_USER@$VPS_IP "cd $VPS_PATH && cp production.env .env"

# Ejecutar despliegue en el VPS
log "Ejecutando despliegue en el VPS..."
ssh $VPS_USER@$VPS_IP "cd $VPS_PATH && ./deploy.sh"

if [ $? -eq 0 ]; then
    log "🎉 ¡Despliegue completado exitosamente!"
    echo ""
    log "🌐 Tu API está disponible en:"
    echo "  • HTTPS: https://$VPS_IP"
    echo "  • Docs:  https://$VPS_IP/docs"
    echo "  • Health: https://$VPS_IP/health"
    echo ""
    log "📊 Para monitorear:"
    echo "  ssh $VPS_USER@$VPS_IP 'cd $VPS_PATH && docker-compose logs -f'"
else
    error "❌ Error en el despliegue. Revisa los logs en el VPS."
    echo "  ssh $VPS_USER@$VPS_IP 'cd $VPS_PATH && docker-compose logs'"
fi
