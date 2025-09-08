yecto# 🚀 Guía de Despliegue en VPS con Docker y HTTPS

Esta guía te ayudará a desplegar la API en tu VPS `34.136.15.241` con Docker, Nginx y SSL automático.

## 📋 Prerrequisitos

### En tu máquina local:
- Git instalado
- Acceso SSH al VPS

### En el VPS (34.136.15.241):
- Docker instalado
- Docker Compose instalado
- Puertos 80 y 443 abiertos
- Dominio apuntando al VPS (opcional, pero recomendado)

## 🛠️ Instalación en el VPS

### 1. Conectarse al VPS
```bash
ssh root@34.136.15.241
# o
ssh usuario@34.136.15.241
```

### 2. Instalar Docker (si no está instalado)
```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### 3. Clonar el proyecto
```bash
# Crear directorio para la aplicación
mkdir -p /opt/alza-api
cd /opt/alza-api

# Clonar o subir archivos del proyecto
# Opción 1: Si tienes Git configurado
git clone <tu-repositorio> .

# Opción 2: Subir archivos manualmente
# scp -r /ruta/local/del/proyecto/* root@34.136.15.241:/opt/alza-api/
```

### 4. Configurar variables de entorno
```bash
# Copiar archivo de configuración
cp production.env .env

# Editar configuración si es necesario
nano .env
```

### 5. Configurar SSL (Importante)
```bash
# Editar el script de SSL con tu email
nano init-letsencrypt.sh

# Cambiar esta línea:
email="admin@example.com"  # Por tu email real
```

### 6. Ejecutar despliegue
```bash
# Hacer ejecutables los scripts
chmod +x deploy.sh
chmod +x init-letsencrypt.sh

# Ejecutar despliegue completo
./deploy.sh
```

## 🔧 Estructura de Archivos

```
/opt/alza-api/
├── Dockerfile              # Imagen de la API
├── docker-compose.yml      # Orquestación de servicios
├── deploy.sh              # Script de despliegue
├── init-letsencrypt.sh    # Configuración SSL
├── nginx/
│   └── nginx.conf         # Configuración Nginx
├── certbot/               # Certificados SSL (auto-generado)
├── logs/                  # Logs de la aplicación
├── main.py               # Código de la API
├── cache_manager.py      # Sistema de cache
├── config.py             # Configuración
└── requirements-windows.txt
```

## 🌐 URLs Disponibles

Después del despliegue exitoso:

- **API Principal**: `https://34.136.15.241/`
- **Documentación**: `https://34.136.15.241/docs`
- **Health Check**: `https://34.136.15.241/health`
- **Cache Stats**: `https://34.136.15.241/cache/stats`

## 📊 Servicios Incluidos

### 🐳 Contenedores Docker:
1. **alza_api** - API FastAPI principal
2. **alza_nginx** - Proxy reverso con SSL
3. **alza_redis** - Cache Redis
4. **alza_certbot** - Renovación automática SSL

### 🔒 Características de Seguridad:
- ✅ HTTPS automático con Let's Encrypt
- ✅ Renovación automática de certificados
- ✅ Headers de seguridad configurados
- ✅ Compresión Gzip habilitada
- ✅ Rate limiting (configurable)

## 🛠️ Comandos de Administración

### Ver estado de servicios:
```bash
cd /opt/alza-api
docker-compose ps
```

### Ver logs:
```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f api
docker-compose logs -f nginx
```

### Reiniciar servicios:
```bash
# Reiniciar todo
docker-compose restart

# Reiniciar servicio específico
docker-compose restart api
```

### Actualizar la aplicación:
```bash
# Detener servicios
docker-compose down

# Actualizar código (git pull o subir archivos nuevos)
git pull  # o subir archivos

# Reconstruir y reiniciar
docker-compose build --no-cache api
docker-compose up -d
```

### Backup de datos:
```bash
# Backup de Redis
docker-compose exec redis redis-cli BGSAVE

# Backup de logs
tar -czf backup-logs-$(date +%Y%m%d).tar.gz logs/
```

## 🔍 Monitoreo y Troubleshooting

### Verificar SSL:
```bash
# Verificar certificado
openssl s_client -connect 34.136.15.241:443 -servername 34.136.15.241

# Verificar renovación automática
docker-compose logs certbot
```

### Verificar conectividad a base de datos:
```bash
# Desde el contenedor de la API
docker-compose exec api python -c "
import asyncpg
import asyncio

async def test():
    conn = await asyncpg.connect(
        host='34.136.15.241',
        port=5666,
        database='apg_database',
        user='apg_adm_v1',
        password='hfuBZyXf4Dni'
    )
    print('✅ Conexión exitosa')
    await conn.close()

asyncio.run(test())
"
```

### Verificar rendimiento:
```bash
# CPU y memoria
docker stats

# Logs de rendimiento de Nginx
tail -f logs/nginx/access.log
```

## 🆘 Problemas Comunes

### 1. Error de SSL:
```bash
# Regenerar certificados
./init-letsencrypt.sh
```

### 2. API no responde:
```bash
# Verificar logs
docker-compose logs api

# Reiniciar API
docker-compose restart api
```

### 3. Nginx no inicia:
```bash
# Verificar configuración
docker-compose exec nginx nginx -t

# Recargar configuración
docker-compose exec nginx nginx -s reload
```

### 4. Base de datos no conecta:
```bash
# Verificar conectividad de red
docker-compose exec api ping 34.136.15.241

# Verificar variables de entorno
docker-compose exec api printenv | grep DB_
```

## 🔄 Actualizaciones Automáticas

Para configurar actualizaciones automáticas, puedes crear un cron job:

```bash
# Editar crontab
crontab -e

# Agregar línea para actualización diaria a las 3 AM
0 3 * * * cd /opt/alza-api && git pull && docker-compose build --no-cache api && docker-compose up -d
```

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica el estado: `docker-compose ps`
3. Verifica la conectividad: `curl -k https://34.136.15.241/health`

¡Tu API está lista para producción con HTTPS! 🎉
