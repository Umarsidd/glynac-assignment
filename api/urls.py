"""
API URLs for the employee management system.
Employee Management System - API URL Configuration

This module defines all REST API endpoints including:
- Employee CRUD operations
- Department management
- Attendance tracking
- Performance reviews
- Salary management
- Analytics and reporting
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet,
    EmployeeViewSet,
    AttendanceViewSet,
    PerformanceViewSet,
    SalaryViewSet,
    AnalyticsView,
    ExportDataView,
    DashboardView,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'performance', PerformanceViewSet)
router.register(r'salary', SalaryViewSet)

app_name = 'api'

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Custom endpoints
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('export/', ExportDataView.as_view(), name='export_data'),
]
