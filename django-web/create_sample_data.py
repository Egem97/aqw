#!/usr/bin/env python
"""
Script para crear datos de prueba para APG PACKING
Ejecutar con: python manage.py runscript create_sample_data
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alzaweb.settings')
django.setup()

from django.contrib.auth.models import User
from apps.management.models import (
    Producto, Proveedor, Lote, ProcesoProduccion,
    ControlCalidad, Costo, Reporte
)


def create_sample_data():
    """Crear datos de prueba"""
    
    print("🌱 Creando datos de prueba para APG PACKING...")
    
    # Obtener o crear usuario admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@apgpacking.com',
            'first_name': 'Administrador',
            'last_name': 'APG',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Usuario admin creado")
    
    # Crear productos
    productos_data = [
        {
            'codigo': 'ARAND001',
            'nombre': 'Arándanos Premium',
            'categoria': 'FRUTAS',
            'unidad_medida': 'KG',
            'precio_base': Decimal('15.50'),
            'descripcion': 'Arándanos frescos de primera calidad para exportación'
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
        {
            'codigo': 'UVA001',
            'nombre': 'Uvas Red Globe',
            'categoria': 'FRUTAS',
            'unidad_medida': 'CAJAS',
            'precio_base': Decimal('25.00'),
            'descripcion': 'Uvas Red Globe para exportación'
        },
        {
            'codigo': 'MANGO001',
            'nombre': 'Mango Kent',
            'categoria': 'FRUTAS',
            'unidad_medida': 'CAJAS',
            'precio_base': Decimal('20.00'),
            'descripcion': 'Mango Kent premium'
        }
    ]
    
    productos_creados = []
    for producto_data in productos_data:
        producto, created = Producto.objects.get_or_create(
            codigo=producto_data['codigo'],
            defaults={**producto_data, 'created_by': admin_user}
        )
        if created:
            print(f"✅ Producto creado: {producto.nombre}")
        productos_creados.append(producto)
    
    # Crear proveedores
    proveedores_data = [
        {
            'codigo': 'PROV001',
            'nombre': 'Agrícola San José',
            'razon_social': 'Agrícola San José S.A.C.',
            'ruc': '20123456789',
            'direccion': 'Av. Agricultura 123, Lima, Perú',
            'telefono': '01-2345678',
            'email': 'contacto@agricolasanjose.com',
            'contacto_principal': 'Juan Pérez',
            'calificacion': 5
        },
        {
            'codigo': 'PROV002',
            'nombre': 'Frutas del Norte',
            'razon_social': 'Frutas del Norte E.I.R.L.',
            'ruc': '20987654321',
            'direccion': 'Jr. Los Frutales 456, Trujillo, Perú',
            'telefono': '044-123456',
            'email': 'ventas@frutasdelnorte.com',
            'contacto_principal': 'María González',
            'calificacion': 4
        },
        {
            'codigo': 'PROV003',
            'nombre': 'Exportadora del Sur',
            'razon_social': 'Exportadora del Sur S.A.',
            'ruc': '20555666777',
            'direccion': 'Av. Industrial 789, Arequipa, Perú',
            'telefono': '054-987654',
            'email': 'info@exportadorasur.com',
            'contacto_principal': 'Carlos Rodriguez',
            'calificacion': 4
        }
    ]
    
    proveedores_creados = []
    for proveedor_data in proveedores_data:
        proveedor, created = Proveedor.objects.get_or_create(
            codigo=proveedor_data['codigo'],
            defaults={**proveedor_data, 'created_by': admin_user}
        )
        if created:
            print(f"✅ Proveedor creado: {proveedor.nombre}")
        proveedores_creados.append(proveedor)
    
    # Crear lotes
    lotes_data = [
        {
            'numero_lote': 'LT2024001',
            'producto': productos_creados[0],  # Arándanos Premium
            'proveedor': proveedores_creados[0],
            'fecha_cosecha': date.today() - timedelta(days=2),
            'fecha_recepcion': date.today() - timedelta(days=1),
            'cantidad': Decimal('1000.00'),
            'peso_bruto': Decimal('1050.00'),
            'peso_neto': Decimal('1000.00'),
            'precio_compra': Decimal('15.50'),
            'calidad': 'PREMIUM',
            'estado': 'EN_PROCESO',
            'observaciones': 'Lote de alta calidad, perfecto para exportación'
        },
        {
            'numero_lote': 'LT2024002',
            'producto': productos_creados[1],  # Arándanos Orgánicos
            'proveedor': proveedores_creados[1],
            'fecha_cosecha': date.today() - timedelta(days=3),
            'fecha_recepcion': date.today() - timedelta(days=2),
            'cantidad': Decimal('800.00'),
            'peso_bruto': Decimal('820.00'),
            'peso_neto': Decimal('800.00'),
            'precio_compra': Decimal('18.00'),
            'calidad': 'PRIMERA',
            'estado': 'PROCESADO',
            'observaciones': 'Certificación orgánica verificada'
        },
        {
            'numero_lote': 'LT2024003',
            'producto': productos_creados[2],  # Fresas
            'proveedor': proveedores_creados[0],
            'fecha_cosecha': date.today() - timedelta(days=1),
            'fecha_recepcion': date.today(),
            'cantidad': Decimal('500.00'),
            'peso_bruto': Decimal('510.00'),
            'peso_neto': Decimal('500.00'),
            'precio_compra': Decimal('12.00'),
            'calidad': 'PRIMERA',
            'estado': 'RECIBIDO',
            'observaciones': 'Fresas frescas de temporada'
        },
        {
            'numero_lote': 'LT2024004',
            'producto': productos_creados[3],  # Uvas
            'proveedor': proveedores_creados[2],
            'fecha_cosecha': date.today() - timedelta(days=4),
            'fecha_recepcion': date.today() - timedelta(days=3),
            'cantidad': Decimal('200.00'),
            'peso_bruto': Decimal('250.00'),
            'peso_neto': Decimal('200.00'),
            'precio_compra': Decimal('25.00'),
            'calidad': 'PREMIUM',
            'estado': 'EMPACADO',
            'observaciones': 'Uvas Red Globe de exportación'
        }
    ]
    
    lotes_creados = []
    for lote_data in lotes_data:
        lote, created = Lote.objects.get_or_create(
            numero_lote=lote_data['numero_lote'],
            defaults={**lote_data, 'created_by': admin_user}
        )
        if created:
            print(f"✅ Lote creado: {lote.numero_lote} - {lote.producto.nombre}")
        lotes_creados.append(lote)
    
    # Crear procesos de producción
    procesos_data = [
        {
            'codigo': 'PROC001',
            'lote': lotes_creados[0],
            'tipo_proceso': 'LAVADO',
            'fecha_inicio': datetime.now() - timedelta(hours=6),
            'fecha_fin': datetime.now() - timedelta(hours=5),
            'operario': admin_user,
            'cantidad_entrada': Decimal('1000.00'),
            'cantidad_salida': Decimal('980.00'),
            'merma': Decimal('20.00'),
            'costo_proceso': Decimal('150.00'),
            'estado': 'COMPLETADO',
            'observaciones': 'Lavado estándar completado'
        },
        {
            'codigo': 'PROC002',
            'lote': lotes_creados[0],
            'tipo_proceso': 'SELECCION',
            'fecha_inicio': datetime.now() - timedelta(hours=4),
            'operario': admin_user,
            'cantidad_entrada': Decimal('980.00'),
            'cantidad_salida': Decimal('950.00'),
            'merma': Decimal('30.00'),
            'costo_proceso': Decimal('200.00'),
            'estado': 'EN_PROCESO',
            'observaciones': 'Selección en progreso'
        },
        {
            'codigo': 'PROC003',
            'lote': lotes_creados[1],
            'tipo_proceso': 'EMPAQUE',
            'fecha_inicio': datetime.now() - timedelta(hours=2),
            'fecha_fin': datetime.now() - timedelta(hours=1),
            'operario': admin_user,
            'cantidad_entrada': Decimal('800.00'),
            'cantidad_salida': Decimal('790.00'),
            'merma': Decimal('10.00'),
            'costo_proceso': Decimal('300.00'),
            'estado': 'COMPLETADO',
            'observaciones': 'Empaque completado para exportación'
        }
    ]
    
    procesos_creados = []
    for proceso_data in procesos_data:
        proceso, created = ProcesoProduccion.objects.get_or_create(
            codigo=proceso_data['codigo'],
            defaults={**proceso_data, 'created_by': admin_user}
        )
        if created:
            print(f"✅ Proceso creado: {proceso.codigo} - {proceso.get_tipo_proceso_display()}")
        procesos_creados.append(proceso)
    
    # Crear controles de calidad
    controles_data = [
        {
            'codigo': 'CC001',
            'lote': lotes_creados[0],
            'proceso': procesos_creados[0],
            'fecha_control': datetime.now() - timedelta(hours=3),
            'inspector': admin_user,
            'parametros_evaluados': {
                'color': 'Excelente',
                'tamaño': 'Uniforme',
                'peso': 'Dentro de rango',
                'firmeza': 'Óptima',
                'brix': '12.5'
            },
            'resultado': 'APROBADO',
            'puntuacion': Decimal('9.2'),
            'observaciones': 'Calidad excelente, apto para exportación premium'
        },
        {
            'codigo': 'CC002',
            'lote': lotes_creados[1],
            'proceso': procesos_creados[2],
            'fecha_control': datetime.now() - timedelta(hours=1),
            'inspector': admin_user,
            'parametros_evaluados': {
                'color': 'Bueno',
                'tamaño': 'Uniforme',
                'peso': 'Dentro de rango',
                'firmeza': 'Buena',
                'certificacion_organica': 'Verificada'
            },
            'resultado': 'APROBADO',
            'puntuacion': Decimal('8.7'),
            'observaciones': 'Calidad buena, certificación orgánica confirmada'
        },
        {
            'codigo': 'CC003',
            'lote': lotes_creados[2],
            'fecha_control': datetime.now() - timedelta(minutes=30),
            'inspector': admin_user,
            'parametros_evaluados': {
                'color': 'Pendiente',
                'tamaño': 'Pendiente',
                'peso': 'Pendiente'
            },
            'resultado': 'PENDIENTE',
            'puntuacion': Decimal('0.0'),
            'observaciones': 'Control de calidad pendiente - recién recibido'
        }
    ]
    
    for control_data in controles_data:
        control, created = ControlCalidad.objects.get_or_create(
            codigo=control_data['codigo'],
            defaults={**control_data, 'created_by': admin_user}
        )
        if created:
            print(f"✅ Control de calidad creado: {control.codigo}")
    
    # Crear costos
    costos_data = [
        {
            'codigo': 'COST001',
            'tipo_costo': 'MATERIA_PRIMA',
            'lote': lotes_creados[0],
            'descripcion': 'Compra arándanos premium',
            'cantidad': Decimal('1000.00'),
            'precio_unitario': Decimal('15.50'),
            'fecha_costo': date.today() - timedelta(days=1),
            'proveedor': proveedores_creados[0],
            'numero_factura': 'F001-2024001'
        },
        {
            'codigo': 'COST002',
            'tipo_costo': 'MANO_OBRA',
            'proceso': procesos_creados[0],
            'descripcion': 'Proceso de lavado',
            'cantidad': Decimal('6.00'),
            'precio_unitario': Decimal('25.00'),
            'fecha_costo': date.today(),
            'numero_factura': 'RH-2024001'
        },
        {
            'codigo': 'COST003',
            'tipo_costo': 'EMPAQUE',
            'proceso': procesos_creados[2],
            'descripcion': 'Material de empaque orgánico',
            'cantidad': Decimal('800.00'),
            'precio_unitario': Decimal('0.35'),
            'fecha_costo': date.today(),
            'numero_factura': 'EMP-2024001'
        }
    ]
    
    for costo_data in costos_data:
        costo, created = Costo.objects.get_or_create(
            codigo=costo_data['codigo'],
            defaults={**costo_data, 'created_by': admin_user}
        )
        if created:
            print(f"✅ Costo creado: {costo.codigo} - {costo.get_tipo_costo_display()}")
    
    print("\n🎉 Datos de prueba creados exitosamente!")
    print("\n📊 Resumen:")
    print(f"  • Productos: {Producto.objects.count()}")
    print(f"  • Proveedores: {Proveedor.objects.count()}")
    print(f"  • Lotes: {Lote.objects.count()}")
    print(f"  • Procesos: {ProcesoProduccion.objects.count()}")
    print(f"  • Controles de calidad: {ControlCalidad.objects.count()}")
    print(f"  • Costos: {Costo.objects.count()}")
    print("\n🔐 Credenciales de acceso:")
    print("  • Usuario: admin")
    print("  • Contraseña: admin123")
    print("\n🌐 Puedes acceder en: http://localhost:8000/")


if __name__ == '__main__':
    create_sample_data()
