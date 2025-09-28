"""
Health check URLs for the core application.
Employee Management System - Health Check Endpoints

This module defines health check URL patterns for monitoring system status.
"""

from django.urls import path
from .views import HealthCheckView

app_name = 'health'

urlpatterns = [
    path('', HealthCheckView.as_view(), name='health_check'),
]
