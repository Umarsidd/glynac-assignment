"""
Django admin configuration for employee management system.
Employee Data Generation & Visualization System - Admin Interface

This module configures the Django admin interface for all employee-related models.
Provides custom admin classes with enhanced functionality including:
- List displays with relevant fields
- Filtering capabilities
- Search functionality
- Inline editing for related models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Department, Employee, Attendance, Performance, Salary


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for Department model."""
    list_display = ['name', 'manager', 'employee_count', 'budget', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'employee_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'manager')
        }),
        ('Financial', {
            'fields': ('budget',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class AttendanceInline(admin.TabularInline):
    """Inline admin for Attendance records."""
    model = Attendance
    extra = 0
    fields = ['date', 'check_in_time', 'check_out_time', 'status', 'hours_worked']
    readonly_fields = ['hours_worked']
    ordering = ['-date']


class PerformanceInline(admin.TabularInline):
    """Inline admin for Performance reviews."""
    model = Performance
    fk_name = 'employee'  # Specify which FK to use
    extra = 0
    fields = ['review_period_end', 'technical_skills', 'communication', 'teamwork', 'leadership', 'overall_rating']
    readonly_fields = ['overall_rating']
    ordering = ['-review_period_end']


class SalaryInline(admin.TabularInline):
    """Inline admin for Salary records."""
    model = Salary
    fk_name = 'employee'  # Specify which FK to use
    extra = 0
    fields = ['effective_date', 'base_salary', 'allowances', 'bonus', 'total_salary', 'salary_type']
    readonly_fields = ['total_salary']
    ordering = ['-effective_date']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin configuration for Employee model."""
    list_display = [
        'employee_id', 'full_name', 'email', 'department', 
        'position', 'salary', 'hire_date', 'years_of_service', 'is_active'
    ]
    list_filter = ['department', 'position', 'is_active', 'hire_date']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']
    ordering = ['employee_id']
    readonly_fields = ['created_at', 'updated_at', 'years_of_service', 'full_name']
    inlines = [AttendanceInline, PerformanceInline, SalaryInline]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone', 'birth_date')
        }),
        ('Employment Details', {
            'fields': ('department', 'position', 'hire_date', 'salary')
        }),
        ('Account', {
            'fields': ('user',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Computed Fields', {
            'fields': ('full_name', 'years_of_service'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        """Display employee's full name."""
        return obj.full_name
    full_name.short_description = 'Full Name'

    def years_of_service(self, obj):
        """Display years of service."""
        return f"{obj.years_of_service} years"
    years_of_service.short_description = 'Years of Service'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin configuration for Attendance model."""
    list_display = [
        'employee', 'date', 'check_in_time', 'check_out_time', 
        'hours_worked', 'status', 'break_duration'
    ]
    list_filter = ['status', 'date', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering = ['-date', 'employee']
    readonly_fields = ['created_at', 'updated_at', 'hours_worked']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Employee & Date', {
            'fields': ('employee', 'date')
        }),
        ('Time Tracking', {
            'fields': ('check_in_time', 'check_out_time', 'break_duration', 'hours_worked')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def hours_worked(self, obj):
        """Display hours worked."""
        return f"{obj.hours_worked:.2f} hours"
    hours_worked.short_description = 'Hours Worked'


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    """Admin configuration for Performance model."""
    list_display = [
        'employee', 'review_period_end', 'overall_rating', 'goals_achieved',
        'technical_skills', 'communication', 'teamwork', 'leadership', 'reviewer'
    ]
    list_filter = ['review_period_end', 'reviewer', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering = ['-review_period_end', 'employee']
    readonly_fields = ['created_at', 'updated_at', 'overall_rating']
    date_hierarchy = 'review_period_end'
    
    fieldsets = (
        ('Review Details', {
            'fields': ('employee', 'reviewer', 'review_period_start', 'review_period_end')
        }),
        ('Performance Ratings', {
            'fields': ('technical_skills', 'communication', 'teamwork', 'leadership', 'overall_rating')
        }),
        ('Goals & Feedback', {
            'fields': ('goals_achieved', 'feedback')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def overall_rating(self, obj):
        """Display overall rating with color coding."""
        rating = obj.overall_rating
        if rating >= 4.5:
            color = 'green'
        elif rating >= 3.5:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.2f}</span>',
            color, rating
        )
    overall_rating.short_description = 'Overall Rating'


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    """Admin configuration for Salary model."""
    list_display = [
        'employee', 'effective_date', 'base_salary', 'total_salary', 
        'salary_type', 'approved_by'
    ]
    list_filter = ['salary_type', 'effective_date', 'approved_by']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering = ['-effective_date', 'employee']
    readonly_fields = ['created_at', 'updated_at', 'total_salary']
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        ('Employee & Date', {
            'fields': ('employee', 'effective_date', 'salary_type')
        }),
        ('Salary Components', {
            'fields': ('base_salary', 'allowances', 'bonus', 'deductions', 'total_salary')
        }),
        ('Approval', {
            'fields': ('approved_by', 'reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_salary(self, obj):
        """Display total salary formatted."""
        return f"${obj.total_salary:,.2f}"
    total_salary.short_description = 'Total Salary'


# Customize admin site header and title
admin.site.site_header = "Employee Management System"
admin.site.site_title = "EMS Admin"
admin.site.index_title = "Welcome to Employee Management System Administration"
