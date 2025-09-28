"""
App configuration for API application.
Employee Management System - API App Configuration
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configuration class for the API application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'API Endpoints'
