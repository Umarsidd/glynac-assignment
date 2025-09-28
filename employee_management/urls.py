"""
URL configuration for employee_management project.
Main URL routing for Employee Data Generation & Visualization System

This module defines the main URL patterns including:
- Admin interface
- API endpoints
- Swagger documentation
- Authentication endpoints
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Employee Management API",
        default_version='v1',
        description="REST API for Employee Data Generation & Visualization System",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="admin@employeemanagement.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/v1/', include('api.urls')),
    
    # Authentication
    path('api/auth/', include('core.urls')),
    
    # Health Check
    path('health/', include('core.health_urls')),
    
    # Swagger Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Root redirect to Swagger
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
