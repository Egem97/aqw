#!/bin/bash

# Script para configurar firewall en VPS Ubuntu
# Ejecutar en el VPS: sudo bash setup-firewall.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[FIREWALL] $1${NC}"; }
warn() { echo -e "${YELLOW}[FIREWALL] WARNING: $1${NC}"; }
error() { echo -e "${RED}[FIREWALL] ERROR: $1${NC}"; }
info() { echo -e "${BLUE}[FIREWALL] INFO: $1${NC}"; }

echo ""
echo "🛡️  Configurando Firewall para Alza API"
echo "======================================="
echo ""

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    error "Este script debe ejecutarse como root"
    echo "Ejecutar: sudo bash setup-firewall.sh"
    exit 1
fi

log "Configurando firewall UFW..."

# Instalar UFW si no está instalado
if ! command -v ufw &> /dev/null; then
    log "Instalando UFW..."
    apt-get update
    apt-get install -y ufw
fi

# Resetear UFW a configuración por defecto
log "Reseteando configuración UFW..."
ufw --force reset

# Configurar políticas por defecto
log "Configurando políticas por defecto..."
ufw default deny incoming
ufw default allow outgoing

# Permitir SSH (CRÍTICO)
log "Permitiendo SSH (Puerto 22)..."
ufw allow 22/tcp
ufw allow ssh

# Permitir HTTP (Puerto 80)
log "Permitiendo HTTP (Puerto 80)..."
ufw allow 80/tcp
ufw allow http

# Permitir HTTPS (Puerto 443)
log "Permitiendo HTTPS (Puerto 443)..."
ufw allow 443/tcp
ufw allow https

# Permitir acceso local (loopback)
log "Permitiendo acceso local..."
ufw allow from 127.0.0.1

# Habilitar UFW
log "Habilitando UFW..."
ufw --force enable

echo ""
log "✅ Firewall configurado correctamente"
echo ""
info "📋 Puertos habilitados:"
echo "  • SSH:   22/tcp  (acceso remoto)"
echo "  • HTTP:  80/tcp  (Nginx)"
echo "  • HTTPS: 443/tcp (Nginx SSL)"
echo ""
info "🔒 Puertos internos (Docker):"
echo "  • FastAPI: 5544 (solo interno)"
echo "  • Django:  8880 (solo interno)"
echo "  • Redis:   6379 (solo interno)"
echo ""

# Mostrar estado del firewall
log "📊 Estado actual del firewall:"
ufw status verbose

echo ""
warn "⚠️  IMPORTANTE:"
echo "  • El puerto 22 (SSH) está habilitado para acceso remoto"
echo "  • Los puertos 80 y 443 están habilitados para el web server"
echo "  • Los servicios Docker usan red interna (no necesitan firewall)"
echo ""
log "🚀 Firewall listo para Alza API"
