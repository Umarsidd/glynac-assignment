"""
App configuration for employees application.
Employee Management System - Employees App Configuration
"""

from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    """Configuration class for the employees application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employees'
    verbose_name = 'Employee Management'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        import employees.signals
