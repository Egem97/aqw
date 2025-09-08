"""
Admin configuration for APG PACKING Management System
Updated for new corporate structure
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Role, Category, Company, Profile


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['description', 'create', 'modified']
    list_filter = ['create', 'modified']
    search_fields = ['description']
    ordering = ['description']
    readonly_fields = ['id', 'create', 'modified']
    
    fieldsets = (
        ('Información del Rol', {
            'fields': ('description', 'avatar_role')
        }),
        ('Metadatos', {
            'fields': ('id', 'create', 'modified'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['description', 'create', 'modified']
    list_filter = ['create', 'modified']
    search_fields = ['description']
    ordering = ['description']
    readonly_fields = ['id', 'create', 'modified']
    
    fieldsets = (
        ('Información de la Categoría', {
            'fields': ('description', 'avatar_category')
        }),
        ('Metadatos', {
            'fields': ('id', 'create', 'modified'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['description', 'ruc', 'category', 'type_con', 'create']
    list_filter = ['category', 'type_con', 'create', 'modified']
    search_fields = ['description', 'ruc', 'phone']
    list_editable = ['type_con']
    ordering = ['description']
    readonly_fields = ['id', 'create', 'modified']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('ruc', 'description', 'phone', 'category', 'avatar_profile')
        }),
        ('Configuración de Conexión API', {
            'fields': ('type_con', 'ip', 'puerto', 'token'),
            'classes': ('collapse',)
        }),
        ('Configuración de Base de Datos', {
            'fields': ('server', 'database', 'uid', 'uid_pass', 'driver'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('id', 'create', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'user', 'company', 'role', 'verified', 'create']
    list_filter = ['verified', 'requested_verified', 'company', 'role', 'create']
    search_fields = ['name', 'surname', 'user__username', 'user__email', 'phone']
    list_editable = ['verified']
    ordering = ['surname', 'name']
    readonly_fields = ['id', 'create', 'modified']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('user', 'name', 'surname', 'phone', 'avatar_profile')
        }),
        ('Información Corporativa', {
            'fields': ('company', 'role')
        }),
        ('Estado de Verificación', {
            'fields': ('verified', 'requested_verified')
        }),
        ('Metadatos', {
            'fields': ('id', 'create', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return f"{obj.surname} {obj.name}"
    get_full_name.short_description = 'Nombre Completo'
    get_full_name.admin_order_field = 'surname'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'company', 'role')


# Customize admin site
admin.site.site_header = "APG PACKING - Administración Corporativa"
admin.site.site_title = "APG PACKING Admin"
admin.site.index_title = "Panel de Administración Corporativa"