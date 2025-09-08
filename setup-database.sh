#!/bin/bash

# Script para configurar la base de datos APG PACKING
# Ejecutar desde el directorio del proyecto

set -e

echo "🗄️  Configurando base de datos APG PACKING..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
if [ ! -f "manage.py" ] && [ ! -d "django-web" ]; then
    error "No se encuentra manage.py ni django-web. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

# Cambiar al directorio de Django
cd django-web

# Verificar conexión a la base de datos
log "Verificando conexión a la base de datos..."
python manage.py check --database default

if [ $? -ne 0 ]; then
    error "No se puede conectar a la base de datos. Verifica las credenciales."
    exit 1
fi

log "✅ Conexión a la base de datos exitosa"

# Crear migraciones
log "Creando migraciones..."
python manage.py makemigrations management

# Aplicar migraciones
log "Aplicando migraciones..."
python manage.py migrate

# Crear superusuario si no existe
log "Configurando superusuario..."
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@apgpacking.com', 'admin123')
    print('✅ Superusuario creado: admin/admin123')
else:
    print('ℹ️  Superusuario ya existe')
EOF

# Recopilar archivos estáticos
log "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear datos de prueba
log "Creando datos de prueba..."
python manage.py shell << EOF
from apps.management.models import Producto, Proveedor, Lote
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal

# Crear productos de prueba
productos_data = [
    {
        'codigo': 'ARAND001',
        'nombre': 'Arándanos Premium',
        'categoria': 'FRUTAS',
        'unidad_medida': 'KG',
        'precio_base': Decimal('15.50'),
        'descripcion': 'Arándanos frescos de primera calidad'
    },
    {
        'codigo': 'ARAND002',
        'nombre': 'Arándanos Orgánicos',
        'categoria': 'FRUTAS',
        'unidad_medida': 'KG',
        'precio_base': Decimal('18.00'),
        'descripcion': 'Arándanos orgánicos certificados'
    },
    {
        'codigo': 'FRESA001',
        'nombre': 'Fresas Frescas',
        'categoria': 'FRUTAS',
        'unidad_medida': 'KG',
        'precio_base': Decimal('12.00'),
        'descripcion': 'Fresas frescas de temporada'
    },
]

for producto_data in productos_data:
    producto, created = Producto.objects.get_or_create(
        codigo=producto_data['codigo'],
        defaults=producto_data
    )
    if created:
        print(f'✅ Producto creado: {producto.nombre}')
    else:
        print(f'ℹ️  Producto ya existe: {producto.nombre}')

# Crear proveedores de prueba
proveedores_data = [
    {
        'codigo': 'PROV001',
        'nombre': 'Agrícola San José',
        'razon_social': 'Agrícola San José S.A.C.',
        'ruc': '20123456789',
        'direccion': 'Av. Agricultura 123, Lima',
        'telefono': '01-2345678',
        'email': 'contacto@agricolasanjose.com',
        'calificacion': 5
    },
    {
        'codigo': 'PROV002',
        'nombre': 'Frutas del Norte',
        'razon_social': 'Frutas del Norte E.I.R.L.',
        'ruc': '20987654321',
        'direccion': 'Jr. Los Frutales 456, Trujillo',
        'telefono': '044-123456',
        'email': 'ventas@frutasdelnorte.com',
        'calificacion': 4
    },
]

for proveedor_data in proveedores_data:
    proveedor, created = Proveedor.objects.get_or_create(
        codigo=proveedor_data['codigo'],
        defaults=proveedor_data
    )
    if created:
        print(f'✅ Proveedor creado: {proveedor.nombre}')
    else:
        print(f'ℹ️  Proveedor ya existe: {proveedor.nombre}')

# Crear algunos lotes de prueba
if Producto.objects.exists() and Proveedor.objects.exists():
    producto = Producto.objects.first()
    proveedor = Proveedor.objects.first()
    admin_user = User.objects.get(username='admin')
    
    lotes_data = [
        {
            'numero_lote': 'LT2024001',
            'producto': producto,
            'proveedor': proveedor,
            'fecha_cosecha': date.today(),
            'cantidad': Decimal('1000.00'),
            'peso_bruto': Decimal('1050.00'),
            'peso_neto': Decimal('1000.00'),
            'precio_compra': Decimal('15.50'),
            'calidad': 'PREMIUM',
            'estado': 'RECIBIDO',
            'created_by': admin_user
        },
    ]
    
    for lote_data in lotes_data:
        lote, created = Lote.objects.get_or_create(
            numero_lote=lote_data['numero_lote'],
            defaults=lote_data
        )
        if created:
            print(f'✅ Lote creado: {lote.numero_lote}')
        else:
            print(f'ℹ️  Lote ya existe: {lote.numero_lote}')

print('✅ Datos de prueba creados exitosamente')
EOF

log "🎉 Base de datos configurada exitosamente!"
echo ""
log "📋 Resumen de la configuración:"
echo "  • Base de datos: apg_crud"
echo "  • Host: 34.136.15.241:5666"
echo "  • Modelos creados y migrados"
echo "  • Superusuario: admin/admin123"
echo "  • Datos de prueba incluidos"
echo ""
log "🌐 URLs disponibles:"
echo "  • Web App: http://localhost:8000/"
echo "  • Admin: http://localhost:8000/admin/"
echo ""
log "🚀 Para iniciar el servidor de desarrollo:"
echo "  cd django-web && python manage.py runserver"
