#!/bin/bash

# Script maestro de despliegue completo
# Ejecutar desde máquina local: bash deploy-all.sh
# Este script limpia, sube y despliega todo automáticamente

set -e

# Configuración
VPS_IP="34.136.15.241"
VPS_USER="egemfelipe"  # Cambiar por tu usuario real
VPS_PATH="/opt/alza-api"
LOCAL_PROJECT_PATH="."

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging functions
log() { echo -e "${GREEN}[DEPLOY] $1${NC}"; }
warn() { echo -e "${YELLOW}[DEPLOY] WARNING: $1${NC}"; }
error() { echo -e "${RED}[DEPLOY] ERROR: $1${NC}"; }
info() { echo -e "${BLUE}[DEPLOY] INFO: $1${NC}"; }
step() { echo -e "${PURPLE}[STEP] $1${NC}"; }

# Banner
clear
echo ""
echo "🚀 ALZA API - DESPLIEGUE COMPLETO"
echo "================================="
echo ""
echo "VPS: $VPS_IP"
echo "Usuario: $VPS_USER"
echo "Ruta: $VPS_PATH"
echo ""

# Confirmar despliegue
read -p "¿Continuar con el despliegue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Despliegue cancelado"
    exit 0
fi

# PASO 1: Limpiar proyecto local
step "PASO 1: Limpiando proyecto local..."
if [ -f "cleanup.sh" ]; then
    chmod +x cleanup.sh
    ./cleanup.sh
else
    warn "cleanup.sh no encontrado, limpiando manualmente..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    rm -rf logs/ 2>/dev/null || true
    mkdir -p logs/{api,django,nginx}
fi

# PASO 2: Verificar archivos necesarios
step "PASO 2: Verificando archivos necesarios..."
required_files=("docker-compose.yml" "production.env" "api/Dockerfile" "django-web/Dockerfile" "nginx/nginx.conf")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        error "Archivo requerido no encontrado: $file"
        exit 1
    fi
done
log "✅ Todos los archivos requeridos encontrados"

# PASO 3: Verificar conectividad VPS
step "PASO 3: Verificando conectividad con VPS..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $VPS_USER@$VPS_IP exit 2>/dev/null; then
    error "No se puede conectar al VPS $VPS_IP"
    echo "Verifica:"
    echo "  • VPS encendido"
    echo "  • Acceso SSH configurado"
    echo "  • IP correcta: $VPS_IP"
    exit 1
fi
log "✅ Conexión VPS exitosa"

# PASO 4: Preparar VPS
step "PASO 4: Preparando VPS..."
info "Instalando dependencias en VPS..."
ssh $VPS_USER@$VPS_IP << 'EOF'
    # Actualizar sistema
    apt-get update -y
    
    # Instalar Docker si no existe
    if ! command -v docker &> /dev/null; then
        echo "Instalando Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
    fi
    
    # Instalar Docker Compose si no existe
    if ! command -v docker-compose &> /dev/null; then
        echo "Instalando Docker Compose..."
        apt-get install -y docker-compose-plugin
    fi
    
    # Instalar utilidades
    apt-get install -y curl tree htop ufw
    
    # Crear directorio del proyecto
    mkdir -p /opt/alza-api
    
    echo "✅ VPS preparado"
EOF

info "Configurando firewall en VPS..."
ssh $VPS_USER@$VPS_IP << 'EOF'
    # Configurar firewall básico
    if command -v ufw &> /dev/null; then
        echo "Configurando UFW..."
        ufw --force reset
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw --force enable
        echo "✅ Firewall configurado"
        ufw status
    fi
EOF

# PASO 5: Subir archivos al VPS
step "PASO 5: Subiendo archivos al VPS..."
info "Sincronizando archivos..."
rsync -avz --progress --delete \
    --exclude='.git/' \
    --exclude='env/' \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='logs/' \
    --exclude='certbot/' \
    --exclude='*.log' \
    --exclude='.env' \
    ./ $VPS_USER@$VPS_IP:$VPS_PATH/

log "✅ Archivos subidos al VPS"

# PASO 6: Configurar permisos y entorno en VPS
step "PASO 6: Configurando entorno en VPS..."
ssh $VPS_USER@$VPS_IP << EOF
    cd $VPS_PATH
    
    # Hacer ejecutables los scripts
    chmod +x *.sh
    
    # Configurar variables de entorno
    cp production.env .env
    
    # Crear estructura de directorios
    mkdir -p logs/{api,django,nginx}
    mkdir -p certbot/{conf,www}
    
    echo "✅ Entorno configurado"
EOF

# PASO 7: Desplegar en VPS
step "PASO 7: Desplegando aplicación en VPS..."
info "Ejecutando despliegue remoto..."

# Ejecutar despliegue en VPS con output en tiempo real
ssh -t $VPS_USER@$VPS_IP << EOF
    cd $VPS_PATH
    
    echo "🚀 Iniciando despliegue en VPS..."
    
    # Usar script simple si existe, sino usar docker-compose directamente
    if [ -f "deploy-simple.sh" ]; then
        ./deploy-simple.sh
    else
        echo "Usando despliegue básico..."
        docker-compose down --remove-orphans || true
        docker-compose build --no-cache
        docker-compose up -d
        sleep 30
        docker-compose ps
    fi
EOF

if [ $? -eq 0 ]; then
    # PASO 8: Verificación final
    step "PASO 8: Verificación final..."
    
    info "Verificando servicios..."
    sleep 10
    
    # Verificar API
    if curl -f http://$VPS_IP:5544/health &>/dev/null; then
        log "✅ API funcionando"
    else
        warn "⚠️  API puede no estar respondiendo"
    fi
    
    # Verificar Nginx
    if curl -f http://$VPS_IP &>/dev/null; then
        log "✅ Nginx funcionando"
    else
        warn "⚠️  Nginx puede no estar respondiendo"
    fi
    
    # Resultado final
    echo ""
    echo "🎉 ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!"
    echo "======================================"
    echo ""
    log "🌐 URLs disponibles:"
    echo "  • API:          http://$VPS_IP:5544"
    echo "  • API Health:   http://$VPS_IP:5544/health"
    echo "  • API Docs:     http://$VPS_IP:5544/docs"
    echo "  • Nginx:        http://$VPS_IP"
    echo ""
    log "📋 Comandos útiles:"
    echo "  • SSH al VPS:   ssh $VPS_USER@$VPS_IP"
    echo "  • Ver logs:     ssh $VPS_USER@$VPS_IP 'cd $VPS_PATH && docker-compose logs -f'"
    echo "  • Estado:       ssh $VPS_USER@$VPS_IP 'cd $VPS_PATH && docker-compose ps'"
    echo "  • Reiniciar:    ssh $VPS_USER@$VPS_IP 'cd $VPS_PATH && docker-compose restart'"
    echo ""
    info "🔐 Para configurar SSL:"
    echo "  ssh $VPS_USER@$VPS_IP 'cd $VPS_PATH && ./init-letsencrypt.sh'"
    echo ""
    log "✅ Despliegue finalizado correctamente"
    
else
    error "❌ Error en el despliegue"
    echo ""
    echo "Para debuggear:"
    echo "  ssh $VPS_USER@$VPS_IP 'cd $VPS_PATH && docker-compose logs'"
    exit 1
fi
