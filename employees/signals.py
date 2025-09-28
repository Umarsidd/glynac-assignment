"""
Django signals for employee management system.
Employee Data Generation & Visualization System - Signal Handlers

This module contains signal handlers for automatic processing when model instances are saved/deleted.
Handles automatic salary updates when employee base salary changes.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Employee, Salary


@receiver(pre_save, sender=Employee)
def update_employee_salary_history(sender, instance, **kwargs):
    """
    Create salary history record when employee salary changes.
    This signal automatically tracks salary changes for audit purposes.
    """
    if instance.pk:  # Only for existing employees
        try:
            old_employee = Employee.objects.get(pk=instance.pk)
            if old_employee.salary != instance.salary:
                # Create new salary record
                Salary.objects.create(
                    employee=instance,
                    effective_date=timezone.now().date(),
                    base_salary=instance.salary,
                    salary_type='adjustment',
                    reason='Automatic salary update via employee record change'
                )
        except Employee.DoesNotExist:
            pass  # New employee, no need to track change
