"""
Views for APG PACKING Corporate Management System
Updated for new corporate structure with Roles, Categories, Companies and Profiles
"""

import json
import logging
import base64
import io
from datetime import datetime, timedelta
from decimal import Decimal
from PIL import Image

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import Role, Category, Company, Profile

logger = logging.getLogger(__name__)


# Image Processing Functions
def process_avatar_image(image_file, max_size=300, quality=85):
    """
    Procesa y redimensiona una imagen para avatar
    Convierte a base64 para almacenar en BD
    """
    try:
        # Abrir imagen con Pillow
        img = Image.open(image_file)
        
        # Convertir a RGB si es necesario (para PNGs con transparencia)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Redimensionar manteniendo aspecto
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Crear imagen cuadrada centrada
        size = max(img.size)
        square_img = Image.new('RGB', (size, size), (255, 255, 255))
        paste_x = (size - img.size[0]) // 2
        paste_y = (size - img.size[1]) // 2
        square_img.paste(img, (paste_x, paste_y))
        
        # Redimensionar a tamaño final
        square_img = square_img.resize((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convertir a base64
        buffer = io.BytesIO()
        square_img.save(buffer, format='JPEG', quality=quality, optimize=True)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{img_str}"
        
    except Exception as e:
        logger.error(f"Error processing avatar image: {e}")
        return None


# Authentication Views
def login_view(request):
    """Corporate login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('management:dashboard')
        else:
            messages.error(request, 'Credenciales inválidas')
    
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('management:login')


# Dashboard Views
@login_required
def dashboard_view(request):
    """Main corporate dashboard"""
    try:
        # Get user profile
        user_profile = None
        try:
            user_profile = Profile.objects.select_related('company', 'role').get(user=request.user)
        except Profile.DoesNotExist:
            messages.warning(request, 'Tu perfil no está configurado. Contacta al administrador.')
        
        # Get statistics
        total_companies = Company.objects.count()
        total_users = Profile.objects.count()
        verified_users = Profile.objects.filter(verified=True).count()
        pending_verifications = Profile.objects.filter(requested_verified=True, verified=False).count()
        
        # Recent data
        recent_companies = Company.objects.select_related('category').order_by('-create')[:5]
        recent_profiles = Profile.objects.select_related('user', 'company', 'role').order_by('-create')[:5]
        
        # Category distribution
        category_stats = Category.objects.annotate(
            company_count=Count('company')
        ).order_by('-company_count')[:5]
        
        # Role distribution
        role_stats = Role.objects.annotate(
            profile_count=Count('profile')
        ).order_by('-profile_count')[:5]
        
        context = {
            'user_profile': user_profile,
            'stats': {
                'total_companies': total_companies,
                'total_users': total_users,
                'verified_users': verified_users,
                'pending_verifications': pending_verifications,
            },
            'recent_companies': recent_companies,
            'recent_profiles': recent_profiles,
            'category_stats': category_stats,
            'role_stats': role_stats,
        }
        
        return render(request, 'management/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        messages.error(request, 'Error al cargar el dashboard')
        return render(request, 'management/dashboard.html', {'stats': {}})


# Company Management Views
@login_required
def companies_list_view(request):
    """Companies list with pagination and filtering"""
    try:
        search_query = request.GET.get('search', '')
        category_filter = request.GET.get('category', '')
        type_filter = request.GET.get('type', '')
        
        # Build query
        queryset = Company.objects.select_related('category')
        
        if search_query:
            queryset = queryset.filter(
                Q(description__icontains=search_query) | 
                Q(ruc__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
            
        if type_filter:
            queryset = queryset.filter(type_con=type_filter)
        
        # Pagination
        companies = queryset.order_by('description')
        paginator = Paginator(companies, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Filter options
        categories = Category.objects.all().order_by('description')
        connection_types = Company._meta.get_field('type_con').choices
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'category_filter': category_filter,
            'type_filter': type_filter,
            'categories': categories,
            'connection_types': connection_types,
        }
        
        return render(request, 'management/companies/list.html', context)
        
    except Exception as e:
        logger.error(f"Companies list error: {e}")
        messages.error(request, 'Error al cargar compañías')
        return render(request, 'management/companies/list.html', {'page_obj': None})


@login_required
def company_detail_view(request, company_id):
    """Company detail view"""
    try:
        company = get_object_or_404(Company.objects.select_related('category'), id=company_id)
        
        # Get company profiles
        profiles = Profile.objects.filter(company=company).select_related('user', 'role').order_by('surname', 'name')
        
        context = {
            'company': company,
            'profiles': profiles,
        }
        
        return render(request, 'management/companies/detail.html', context)
        
    except Exception as e:
        logger.error(f"Company detail error: {e}")
        messages.error(request, 'Error al cargar detalles de la compañía')
        return redirect('management:companies_list')


# Profile Management Views
@login_required
def profiles_list_view(request):
    """Profiles list with filtering"""
    try:
        search_query = request.GET.get('search', '')
        company_filter = request.GET.get('company', '')
        role_filter = request.GET.get('role', '')
        verified_filter = request.GET.get('verified', '')
        
        # Build query
        queryset = Profile.objects.select_related('user', 'company', 'role')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(surname__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        if company_filter:
            queryset = queryset.filter(company_id=company_filter)
            
        if role_filter:
            queryset = queryset.filter(role_id=role_filter)
            
        if verified_filter:
            if verified_filter == 'verified':
                queryset = queryset.filter(verified=True)
            elif verified_filter == 'pending':
                queryset = queryset.filter(requested_verified=True, verified=False)
            elif verified_filter == 'unverified':
                queryset = queryset.filter(verified=False)
        
        # Pagination
        profiles = queryset.order_by('surname', 'name')
        paginator = Paginator(profiles, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Filter options
        companies = Company.objects.all().order_by('description')
        roles = Role.objects.all().order_by('description')
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'company_filter': company_filter,
            'role_filter': role_filter,
            'verified_filter': verified_filter,
            'companies': companies,
            'roles': roles,
        }
        
        return render(request, 'management/profiles/list.html', context)
        
    except Exception as e:
        logger.error(f"Profiles list error: {e}")
        messages.error(request, 'Error al cargar perfiles')
        return render(request, 'management/profiles/list.html', {'page_obj': None})


@login_required
def profile_detail_view(request, profile_id):
    """Profile detail view"""
    try:
        profile = get_object_or_404(
            Profile.objects.select_related('user', 'company', 'role'), 
            id=profile_id
        )
        
        context = {
            'profile': profile,
        }
        
        return render(request, 'management/profiles/detail.html', context)
        
    except Exception as e:
        logger.error(f"Profile detail error: {e}")
        messages.error(request, 'Error al cargar detalles del perfil')
        return redirect('management:profiles_list')


# Role Management Views
@login_required
def roles_list_view(request):
    """Roles list with profile count"""
    try:
        search_query = request.GET.get('search', '')
        
        # Build query
        queryset = Role.objects.annotate(profile_count=Count('profile'))
        
        if search_query:
            queryset = queryset.filter(description__icontains=search_query)
        
        # Pagination
        roles = queryset.order_by('description')
        paginator = Paginator(roles, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
        }
        
        return render(request, 'management/roles/list.html', context)
        
    except Exception as e:
        logger.error(f"Roles list error: {e}")
        messages.error(request, 'Error al cargar roles')
        return render(request, 'management/roles/list.html', {'page_obj': None})


# Category Management Views
@login_required
def categories_list_view(request):
    """Categories list with company count"""
    try:
        search_query = request.GET.get('search', '')
        
        # Build query
        queryset = Category.objects.annotate(company_count=Count('company'))
        
        if search_query:
            queryset = queryset.filter(description__icontains=search_query)
        
        # Pagination
        categories = queryset.order_by('description')
        paginator = Paginator(categories, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
        }
        
        return render(request, 'management/categories/list.html', context)
        
    except Exception as e:
        logger.error(f"Categories list error: {e}")
        messages.error(request, 'Error al cargar categorías')
        return render(request, 'management/categories/list.html', {'page_obj': None})


# API Endpoints for AJAX calls
@csrf_exempt
@require_http_methods(["GET"])
def api_dashboard_stats(request):
    """API endpoint for dashboard stats"""
    try:
        # Calculate stats
        total_companies = Company.objects.count()
        total_users = Profile.objects.count()
        verified_users = Profile.objects.filter(verified=True).count()
        pending_verifications = Profile.objects.filter(requested_verified=True, verified=False).count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_companies': total_companies,
                'total_users': total_users,
                'verified_users': verified_users,
                'pending_verifications': pending_verifications,
                'timestamp': datetime.now().isoformat(),
            }
        })
        
    except Exception as e:
        logger.error(f"API dashboard stats error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_verify_profile(request):
    """API endpoint for verifying profiles"""
    try:
        data = json.loads(request.body)
        profile_id = data.get('profile_id')
        verified = data.get('verified', False)
        
        # Update profile
        profile = Profile.objects.get(id=profile_id)
        profile.verified = verified
        if verified:
            profile.requested_verified = False
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Perfil {"verificado" if verified else "no verificado"} exitosamente',
            'data': {
                'profile_id': profile_id,
                'verified': verified,
                'updated_at': datetime.now().isoformat(),
            }
        })
        
    except Exception as e:
        logger.error(f"API verify profile error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Verification Management
@login_required
def verification_requests_view(request):
    """View for managing verification requests"""
    try:
        # Get pending verification requests
        pending_profiles = Profile.objects.filter(
            requested_verified=True, 
            verified=False
        ).select_related('user', 'company', 'role').order_by('create')
        
        # Pagination
        paginator = Paginator(pending_profiles, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
        }
        
        return render(request, 'management/verification/requests.html', context)
        
    except Exception as e:
        logger.error(f"Verification requests error: {e}")
        messages.error(request, 'Error al cargar solicitudes de verificación')
        return render(request, 'management/verification/requests.html', {'page_obj': None})


# Reports Views
@login_required
def reports_view(request):
    """Corporate reports dashboard"""
    try:
        # Company statistics
        company_stats = {
            'total': Company.objects.count(),
            'by_category': list(Category.objects.annotate(
                count=Count('company')
            ).values('description', 'count').order_by('-count')),
            'by_connection_type': list(Company.objects.values('type_con').annotate(
                count=Count('id')
            ).order_by('-count')),
        }
        
        # Profile statistics
        profile_stats = {
            'total': Profile.objects.count(),
            'verified': Profile.objects.filter(verified=True).count(),
            'pending_verification': Profile.objects.filter(requested_verified=True, verified=False).count(),
            'by_role': list(Role.objects.annotate(
                count=Count('profile')
            ).values('description', 'count').order_by('-count')),
        }
        
        # Growth statistics (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        growth_stats = {
            'new_companies': Company.objects.filter(create__gte=thirty_days_ago).count(),
            'new_profiles': Profile.objects.filter(create__gte=thirty_days_ago).count(),
        }
        
        context = {
            'company_stats': company_stats,
            'profile_stats': profile_stats,
            'growth_stats': growth_stats,
        }
        
        return render(request, 'management/reports/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Reports view error: {e}")
        messages.error(request, 'Error al cargar reportes')
        return render(request, 'management/reports/dashboard.html', {})


# Profile Management Views
@login_required
def edit_profile_view(request):
    """Edit user profile view"""
    try:
        # Obtener o crear perfil del usuario
        try:
            profile = Profile.objects.select_related('user', 'company', 'role').get(user=request.user)
        except Profile.DoesNotExist:
            messages.error(request, 'Tu perfil no está configurado. Contacta al administrador.')
            return redirect('management:dashboard')
        
        if request.method == 'POST':
            # Obtener datos del formulario
            name = request.POST.get('name', '').strip()
            surname = request.POST.get('surname', '').strip()
            phone = request.POST.get('phone', '').strip()
            avatar_file = request.FILES.get('avatar')
            
            # Validaciones básicas
            if not name or not surname:
                messages.error(request, 'El nombre y apellido son obligatorios.')
                return render(request, 'management/profile/edit.html', {'profile': profile})
            
            # Procesar avatar si se subió uno nuevo
            avatar_base64 = None
            if avatar_file:
                # Validar tamaño (max 5MB)
                if avatar_file.size > 5 * 1024 * 1024:
                    messages.error(request, 'La imagen es muy grande. Máximo 5MB.')
                    return render(request, 'management/profile/edit.html', {'profile': profile})
                
                # Validar formato
                allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if avatar_file.content_type not in allowed_formats:
                    messages.error(request, 'Formato de imagen no válido. Usa JPG, PNG, GIF o WebP.')
                    return render(request, 'management/profile/edit.html', {'profile': profile})
                
                # Procesar imagen
                avatar_base64 = process_avatar_image(avatar_file)
                if not avatar_base64:
                    messages.error(request, 'Error al procesar la imagen. Intenta con otra.')
                    return render(request, 'management/profile/edit.html', {'profile': profile})
            
            # Actualizar perfil
            try:
                with transaction.atomic():
                    profile.name = name
                    profile.surname = surname
                    profile.phone = phone
                    
                    if avatar_base64:
                        profile.avatar_profile = avatar_base64
                    
                    profile.save()
                    
                    # Actualizar también el usuario de Django
                    request.user.first_name = name
                    request.user.last_name = surname
                    request.user.save()
                    
                    messages.success(request, 'Perfil actualizado exitosamente.')
                    return redirect('management:edit_profile')
                    
            except Exception as e:
                logger.error(f"Error updating profile: {e}")
                messages.error(request, 'Error al actualizar el perfil.')
        
        # Obtener datos para el formulario
        companies = Company.objects.all().order_by('description')
        roles = Role.objects.all().order_by('description')
        
        context = {
            'profile': profile,
            'companies': companies,
            'roles': roles,
        }
        
        return render(request, 'management/profile/edit.html', context)
        
    except Exception as e:
        logger.error(f"Edit profile error: {e}")
        messages.error(request, 'Error al cargar el perfil')
        return redirect('management:dashboard')


@login_required
def view_profile_view(request):
    """View user profile"""
    try:
        profile = Profile.objects.select_related('user', 'company', 'role').get(user=request.user)
        
        context = {
            'profile': profile,
        }
        
        return render(request, 'management/profile/view.html', context)
        
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil no está configurado. Contacta al administrador.')
        return redirect('management:dashboard')
    except Exception as e:
        logger.error(f"View profile error: {e}")
        messages.error(request, 'Error al cargar el perfil')
        return redirect('management:dashboard')


# AJAX endpoint for avatar upload
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def upload_avatar_ajax(request):
    """AJAX endpoint for avatar upload"""
    try:
        profile = Profile.objects.get(user=request.user)
        avatar_file = request.FILES.get('avatar')
        
        if not avatar_file:
            return JsonResponse({'success': False, 'error': 'No se recibió ninguna imagen'})
        
        # Validar tamaño
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'La imagen es muy grande. Máximo 5MB.'})
        
        # Validar formato
        allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_formats:
            return JsonResponse({'success': False, 'error': 'Formato no válido. Usa JPG, PNG, GIF o WebP.'})
        
        # Procesar imagen
        avatar_base64 = process_avatar_image(avatar_file)
        if not avatar_base64:
            return JsonResponse({'success': False, 'error': 'Error al procesar la imagen'})
        
        # Guardar en base de datos
        profile.avatar_profile = avatar_base64
        profile.save()
        
        return JsonResponse({
            'success': True,
            'avatar_url': avatar_base64,
            'message': 'Avatar actualizado exitosamente'
        })
        
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Perfil no encontrado'})
    except Exception as e:
        logger.error(f"Upload avatar error: {e}")
        return JsonResponse({'success': False, 'error': 'Error interno del servidor'})