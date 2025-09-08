#!/usr/bin/env python
"""
Script para crear datos de prueba para el sistema corporativo APG PACKING
Ejecutar con: python create_corporate_data.py
"""

import os
import sys
import django
from datetime import date, datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alzaweb.settings')
django.setup()

from django.contrib.auth.models import User
from apps.management.models import Role, Category, Company, Profile


def create_corporate_data():
    """Crear datos de prueba para el sistema corporativo"""
    
    print("🏢 Creando datos corporativos para APG PACKING...")
    
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
    
    # Crear roles
    roles_data = [
        {
            'description': 'Administrador',
            'avatar_role': '👨‍💼'
        },
        {
            'description': 'Gerente',
            'avatar_role': '🎯'
        },
        {
            'description': 'Supervisor',
            'avatar_role': '👥'
        },
        {
            'description': 'Operador',
            'avatar_role': '⚙️'
        },
        {
            'description': 'Analista',
            'avatar_role': '📊'
        }
    ]
    
    roles_creados = []
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            description=role_data['description'],
            defaults=role_data
        )
        if created:
            print(f"✅ Rol creado: {role.description}")
        roles_creados.append(role)
    
    # Crear categorías
    categories_data = [
        {
            'description': 'Agricultura',
            'avatar_category': '🌱'
        },
        {
            'description': 'Exportación',
            'avatar_category': '🚢'
        },
        {
            'description': 'Procesamiento',
            'avatar_category': '🏭'
        },
        {
            'description': 'Logística',
            'avatar_category': '🚚'
        },
        {
            'description': 'Tecnología',
            'avatar_category': '💻'
        }
    ]
    
    categories_creadas = []
    for category_data in categories_data:
        category, created = Category.objects.get_or_create(
            description=category_data['description'],
            defaults=category_data
        )
        if created:
            print(f"✅ Categoría creada: {category.description}")
        categories_creadas.append(category)
    
    # Crear compañías
    companies_data = [
        {
            'ruc': '20123456789',
            'description': 'APG Packing S.A.C.',
            'phone': '01-2345678',
            'category': categories_creadas[0],  # Agricultura
            'type_con': 'Api',
            'ip': '192.168.1.100',
            'puerto': '8080',
            'avatar_profile': '🏢'
        },
        {
            'ruc': '20987654321',
            'description': 'Exportadora del Norte E.I.R.L.',
            'phone': '044-123456',
            'category': categories_creadas[1],  # Exportación
            'type_con': 'Server Sql',
            'server': 'sql.exportadora.com',
            'database': 'exportadora_db',
            'uid': 'sa',
            'avatar_profile': '🌍'
        },
        {
            'ruc': '20555666777',
            'description': 'Procesadora Agrícola del Sur S.A.',
            'phone': '054-987654',
            'category': categories_creadas[2],  # Procesamiento
            'type_con': 'Api',
            'ip': '10.0.0.50',
            'puerto': '3000',
            'token': 'proc_token_123',
            'avatar_profile': '⚙️'
        },
        {
            'ruc': '20111222333',
            'description': 'Logística Integral Lima S.R.L.',
            'phone': '01-9876543',
            'category': categories_creadas[3],  # Logística
            'type_con': 'Api',
            'ip': '172.16.0.10',
            'puerto': '5000',
            'avatar_profile': '🚛'
        },
        {
            'ruc': '20444555666',
            'description': 'TechAgro Solutions E.I.R.L.',
            'phone': '01-5551234',
            'category': categories_creadas[4],  # Tecnología
            'type_con': 'Server Sql',
            'server': 'db.techagro.com',
            'database': 'techagro_main',
            'uid': 'admin',
            'avatar_profile': '🖥️'
        }
    ]
    
    companies_creadas = []
    for company_data in companies_data:
        company, created = Company.objects.get_or_create(
            ruc=company_data['ruc'],
            defaults=company_data
        )
        if created:
            print(f"✅ Compañía creada: {company.description}")
        companies_creadas.append(company)
    
    # Crear usuarios adicionales
    users_data = [
        {
            'username': 'jperez',
            'email': 'jperez@apgpacking.com',
            'first_name': 'Juan',
            'last_name': 'Pérez'
        },
        {
            'username': 'mgonzalez',
            'email': 'mgonzalez@exportadora.com',
            'first_name': 'María',
            'last_name': 'González'
        },
        {
            'username': 'crodriguez',
            'email': 'crodriguez@procesadora.com',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez'
        },
        {
            'username': 'asanchez',
            'email': 'asanchez@logistica.com',
            'first_name': 'Ana',
            'last_name': 'Sánchez'
        },
        {
            'username': 'lmartinez',
            'email': 'lmartinez@techagro.com',
            'first_name': 'Luis',
            'last_name': 'Martínez'
        }
    ]
    
    users_creados = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"✅ Usuario creado: {user.username}")
        users_creados.append(user)
    
    # Crear perfiles
    profiles_data = [
        {
            'user': admin_user,
            'name': 'Administrador',
            'surname': 'Sistema',
            'company': companies_creadas[0],
            'role': roles_creados[0],  # Administrador
            'verified': True,
            'phone': '999123456',
            'avatar_profile': '👨‍💼'
        },
        {
            'user': users_creados[0],
            'name': 'Juan Carlos',
            'surname': 'Pérez García',
            'company': companies_creadas[0],
            'role': roles_creados[1],  # Gerente
            'verified': True,
            'phone': '999234567',
            'avatar_profile': '🎯'
        },
        {
            'user': users_creados[1],
            'name': 'María Elena',
            'surname': 'González López',
            'company': companies_creadas[1],
            'role': roles_creados[1],  # Gerente
            'verified': True,
            'phone': '999345678',
            'avatar_profile': '🌍'
        },
        {
            'user': users_creados[2],
            'name': 'Carlos Alberto',
            'surname': 'Rodríguez Mendoza',
            'company': companies_creadas[2],
            'role': roles_creados[2],  # Supervisor
            'verified': False,
            'requested_verified': True,
            'phone': '999456789',
            'avatar_profile': '⚙️'
        },
        {
            'user': users_creados[3],
            'name': 'Ana Patricia',
            'surname': 'Sánchez Vargas',
            'company': companies_creadas[3],
            'role': roles_creados[3],  # Operador
            'verified': True,
            'phone': '999567890',
            'avatar_profile': '🚛'
        },
        {
            'user': users_creados[4],
            'name': 'Luis Fernando',
            'surname': 'Martínez Torres',
            'company': companies_creadas[4],
            'role': roles_creados[4],  # Analista
            'verified': False,
            'requested_verified': True,
            'phone': '999678901',
            'avatar_profile': '💻'
        }
    ]
    
    for profile_data in profiles_data:
        profile, created = Profile.objects.get_or_create(
            user=profile_data['user'],
            defaults=profile_data
        )
        if created:
            print(f"✅ Perfil creado: {profile.surname} {profile.name}")
    
    print("\n🎉 Datos corporativos creados exitosamente!")
    print("\n📊 Resumen:")
    print(f"  • Roles: {Role.objects.count()}")
    print(f"  • Categorías: {Category.objects.count()}")
    print(f"  • Compañías: {Company.objects.count()}")
    print(f"  • Perfiles: {Profile.objects.count()}")
    print(f"  • Usuarios: {User.objects.count()}")
    
    print("\n🔐 Credenciales de acceso:")
    print("  • Usuario admin: admin / admin123")
    print("  • Usuario gerente: jperez / password123")
    print("  • Usuario exportación: mgonzalez / password123")
    
    print(f"\n📈 Verificaciones pendientes: {Profile.objects.filter(requested_verified=True, verified=False).count()}")
    print("\n🌐 Puedes acceder en: http://localhost:8000/")


if __name__ == '__main__':
    create_corporate_data()
