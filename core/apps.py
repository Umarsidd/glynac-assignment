"""
App configuration for core application.
Employee Management System - Core App Configuration
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration class for the core application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core System'
