"""
URL configuration for APG Packing alzaweb project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_management(request):
    """Redirect root to management login"""
    return redirect('management:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_management),
    path('auth/', include('apps.management.urls')),
    path('management/', include('apps.management.urls')),
]

# Serve static and media files (siempre, no solo en DEBUG)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)