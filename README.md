# Alza API - Sistema Completo

Sistema completo que incluye FastAPI para consultas de imágenes y datos, más Django Web para gestión administrativa.

## 🚀 Despliegue Rápido en VPS Ubuntu

### Opción 1: Despliegue Automático (Recomendado)
```bash
# Desde tu máquina local, ejecuta un solo comando:
bash deploy-all.sh
```

### Opción 2: Despliegue Manual
```bash
# 1. Limpiar proyecto
bash cleanup.sh

# 2. Subir al VPS
bash upload-to-vps.sh

# 3. En el VPS, ejecutar:
bash deploy-simple.sh
```

## 📋 Requisitos del VPS

- Ubuntu 20.04 o superior
- Docker y Docker Compose (se instalan automáticamente)
- Acceso SSH configurado
- Puertos 80 y 443 abiertos

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Nginx         │    │   Django Web     │    │   FastAPI       │
│   (Gateway)     │────│   (Admin)        │────│   (API REST)    │
│   Port 80/443   │    │   Port 8000      │    │   Port 5544     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────────┐    ┌─────────────────┐
                    │   PostgreSQL    │    │   Redis         │
                    │   (Externo)     │    │   (Cache)       │
                    │   Port 5666     │    │   Port 6379     │
                    └─────────────────┘    └─────────────────┘
```

## 📊 Endpoints Disponibles

### FastAPI (API REST)
- **Base URL**: `http://tu-vps:5544`
- **Docs**: `http://tu-vps:5544/docs`
- **Health**: `http://tu-vps:5544/health`

#### Presentaciones
- `GET /presentaciones` - Obtener todas las presentaciones
- `GET /presentaciones/{id}` - Obtener presentación por ID
- `POST /presentaciones` - Crear presentación
- `PUT /presentaciones/{id}` - Actualizar presentación
- `DELETE /presentaciones/{id}` - Eliminar presentación

#### PHL PT All Tabla
- `GET /phl-pt-all-tabla` - Obtener todos los registros
- `GET /phl-pt-all-tabla/by-date-range` - Filtrar por rango de fechas

#### Imágenes
- `POST /images/by-folder` - Obtener imágenes por folder
- `GET /folders` - Obtener lista de folders

### Django Web (Admin)
- **Base URL**: `http://tu-vps:8880`
- **Admin**: `http://tu-vps:8880/admin/`

## 🔧 Configuración

### Variables de Entorno (production.env)
```env
# Base de datos
DB_HOST=34.136.15.241
DB_PORT=5666
DB_NAME=apg_database
DB_USER=apg_adm_v1
DB_PASSWORD=hfuBZyXf4Dni

# API
API_HOST=0.0.0.0
API_PORT=5544

# Cache
CACHE_ENABLED=true
REDIS_URL=redis://redis:6379

# Seguridad
ALLOWED_HOSTS=34.136.15.241,localhost,127.0.0.1
```

## 📋 Comandos Útiles

### En el VPS
```bash
# Ver estado de servicios
docker-compose ps

# Ver logs
docker-compose logs -f api
docker-compose logs -f django-web
docker-compose logs -f

# Reiniciar servicios
docker-compose restart
docker-compose restart api

# Detener todo
docker-compose down

# Reconstruir y reiniciar
docker-compose up -d --build
```

### Desde máquina local
```bash
# SSH al VPS
ssh root@34.136.15.241

# Ver logs remotos
ssh root@34.136.15.241 'cd /opt/alza-api && docker-compose logs -f'

# Reiniciar servicios remotos
ssh root@34.136.15.241 'cd /opt/alza-api && docker-compose restart'
```

## 🔐 SSL (HTTPS)

Para configurar SSL con Let's Encrypt:
```bash
# En el VPS
./init-letsencrypt.sh
```

## 🐛 Troubleshooting

### API no responde
```bash
# Ver logs de la API
docker-compose logs api

# Verificar salud de la API
curl http://localhost:5544/health

# Reiniciar API
docker-compose restart api
```

### Django no responde
```bash
# Ver logs de Django
docker-compose logs django-web

# Ejecutar migraciones
docker-compose exec django-web python manage.py migrate

# Reiniciar Django
docker-compose restart django-web
```

### Base de datos no conecta
```bash
# Verificar conectividad
docker-compose exec api python -c "
import asyncpg
import asyncio
from config import settings
async def test():
    conn = await asyncpg.connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password
    )
    print('Conexión exitosa')
    await conn.close()
asyncio.run(test())
"
```

## 📦 Estructura del Proyecto

```
alza_api/
├── api/                    # FastAPI Application
│   ├── main.py            # Endpoints principales
│   ├── config.py          # Configuración
│   ├── cache_manager.py   # Gestión de cache
│   ├── requirements.txt   # Dependencias Python
│   └── Dockerfile         # Imagen Docker
├── django-web/            # Django Application
│   ├── manage.py          # Django CLI
│   ├── requirements.txt   # Dependencias Python
│   └── Dockerfile         # Imagen Docker
├── nginx/                 # Nginx Configuration
│   └── nginx.conf         # Configuración Nginx
├── docker-compose.yml     # Orquestación de servicios
├── production.env         # Variables de producción
├── deploy-all.sh          # Script de despliegue completo
├── deploy-simple.sh       # Script de despliegue simple
├── cleanup.sh             # Script de limpieza
└── README.md              # Esta documentación
```

## 🎯 Desarrollo

### Desarrollo Local
```bash
# API
cd api
python -m venv env
source env/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py

# Django
cd django-web
python -m venv env
source env/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py runserver
```

### Testing
```bash
# Test API health
curl http://localhost:5544/health

# Test endpoints
curl http://localhost:5544/presentaciones
curl "http://localhost:5544/phl-pt-all-tabla/by-date-range?fecha_inicio=2024-01-01&fecha_fin=2024-01-31"
```

## 📞 Soporte

Para problemas o preguntas sobre el despliegue:
1. Verificar logs: `docker-compose logs -f`
2. Verificar estado: `docker-compose ps`
3. Reiniciar servicios: `docker-compose restart`

## 📄 Licencia

Proyecto interno - Alza API System