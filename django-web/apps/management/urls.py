"""
URLs for APG PACKING Corporate Management System
Updated for new corporate structure
"""

from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Companies Management
    path('companies/', views.companies_list_view, name='companies_list'),
    path('companies/<uuid:company_id>/', views.company_detail_view, name='company_detail'),
    
    # Profiles Management
    path('profiles/', views.profiles_list_view, name='profiles_list'),
    path('profiles/<uuid:profile_id>/', views.profile_detail_view, name='profile_detail'),
    
    # Roles Management
    path('roles/', views.roles_list_view, name='roles_list'),
    
    # Categories Management
    path('categories/', views.categories_list_view, name='categories_list'),
    
    # Verification Management
    path('verification/', views.verification_requests_view, name='verification_requests'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    
    # Profile Management
    path('profile/', views.view_profile_view, name='view_profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # API Endpoints
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/verify-profile/', views.api_verify_profile, name='api_verify_profile'),
    path('api/upload-avatar/', views.upload_avatar_ajax, name='upload_avatar_ajax'),
]