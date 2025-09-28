"""
API views for employee management system.
Employee Management System - REST API Views

This module contains all REST API views including:
- ViewSets for CRUD operations
- Custom analytics and reporting endpoints
- Data export functionality
- Dashboard data aggregation
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db.models import Avg, Count, Sum, Q
from django.http import HttpResponse
from datetime import date, timedelta
import pandas as pd
import json
import logging

from employees.models import Department, Employee, Attendance, Performance, Salary
from .serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    EmployeeDetailSerializer,
    AttendanceSerializer,
    PerformanceSerializer,
    SalarySerializer,
    AnalyticsSerializer,
)

logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='user', rate='100/hour', method='ALL'), name='dispatch')
class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department model.
    Provides CRUD operations for department management.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active', 'manager']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'budget', 'employee_count']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get all employees in this department."""
        department = self.get_object()
        employees = department.employees.filter(is_active=True)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get department statistics."""
        department = self.get_object()
        employees = department.employees.filter(is_active=True)
        
        stats = {
            'total_employees': employees.count(),
            'average_salary': employees.aggregate(avg_salary=Avg('salary'))['avg_salary'] or 0,
            'positions': employees.values('position').annotate(count=Count('position')),
            'recent_hires': employees.filter(
                hire_date__gte=date.today() - timedelta(days=90)
            ).count(),
        }
        return Response(stats)


@method_decorator(ratelimit(key='user', rate='100/hour', method='ALL'), name='dispatch')
class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Employee model.
    Provides CRUD operations for employee management with detailed information.
    """
    queryset = Employee.objects.select_related('department', 'user').all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['department', 'position', 'is_active']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']
    ordering_fields = ['employee_id', 'hire_date', 'salary', 'created_at']
    ordering = ['employee_id']

    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return EmployeeDetailSerializer
        return EmployeeSerializer

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        """Get attendance summary for an employee."""
        employee = self.get_object()
        thirty_days_ago = date.today() - timedelta(days=30)
        
        attendance_records = employee.attendance_records.filter(date__gte=thirty_days_ago)
        
        summary = {
            'total_days': attendance_records.count(),
            'present_days': attendance_records.filter(status='present').count(),
            'absent_days': attendance_records.filter(status='absent').count(),
            'late_days': attendance_records.filter(status='late').count(),
            'average_hours': attendance_records.aggregate(
                avg_hours=Avg('check_out_time')
            )['avg_hours'] or 0,
            'attendance_rate': 0
        }
        
        if summary['total_days'] > 0:
            summary['attendance_rate'] = (summary['present_days'] / summary['total_days']) * 100
            
        return Response(summary)

    @action(detail=True, methods=['get'])
    def performance_history(self, request, pk=None):
        """Get performance review history for an employee."""
        employee = self.get_object()
        reviews = employee.performance_reviews.order_by('-review_period_end')
        serializer = PerformanceSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def salary_history(self, request, pk=None):
        """Get salary history for an employee."""
        employee = self.get_object()
        salary_records = employee.salary_history.order_by('-effective_date')
        serializer = SalarySerializer(salary_records, many=True)
        return Response(serializer.data)


@method_decorator(ratelimit(key='user', rate='200/hour', method='ALL'), name='dispatch')
class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Attendance model.
    Provides CRUD operations for attendance tracking.
    """
    queryset = Attendance.objects.select_related('employee').all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['employee', 'status', 'date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['date', 'employee', 'status']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        """Get daily attendance report."""
        target_date = request.query_params.get('date', date.today())
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)
            
        attendance_records = self.queryset.filter(date=target_date)
        
        report = {
            'date': target_date,
            'total_employees': Employee.objects.filter(is_active=True).count(),
            'present': attendance_records.filter(status='present').count(),
            'absent': attendance_records.filter(status='absent').count(),
            'late': attendance_records.filter(status='late').count(),
            'on_leave': attendance_records.filter(
                status__in=['sick_leave', 'vacation', 'holiday']
            ).count(),
            'records': AttendanceSerializer(attendance_records, many=True).data
        }
        
        return Response(report)


@method_decorator(ratelimit(key='user', rate='50/hour', method='ALL'), name='dispatch')
class PerformanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Performance model.
    Provides CRUD operations for performance review management.
    """
    queryset = Performance.objects.select_related('employee', 'reviewer').all()
    serializer_class = PerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['employee', 'reviewer', 'review_period_end']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['review_period_end', 'overall_rating']
    ordering = ['-review_period_end']

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get performance analytics across the organization."""
        reviews = self.queryset.all()
        
        analytics = {
            'total_reviews': reviews.count(),
            'average_overall_rating': reviews.aggregate(
                avg_rating=Avg('technical_skills')
            )['avg_rating'] or 0,
            'rating_distribution': {
                'excellent': reviews.filter(technical_skills__gte=4.5).count(),
                'good': reviews.filter(technical_skills__gte=3.5, technical_skills__lt=4.5).count(),
                'average': reviews.filter(technical_skills__gte=2.5, technical_skills__lt=3.5).count(),
                'poor': reviews.filter(technical_skills__lt=2.5).count(),
            },
            'department_performance': reviews.values(
                'employee__department__name'
            ).annotate(
                avg_rating=Avg('technical_skills'),
                count=Count('id')
            ).order_by('-avg_rating')
        }
        
        return Response(analytics)


@method_decorator(ratelimit(key='user', rate='50/hour', method='ALL'), name='dispatch')
class SalaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Salary model.
    Provides CRUD operations for salary management.
    """
    queryset = Salary.objects.select_related('employee', 'approved_by').all()
    serializer_class = SalarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['employee', 'salary_type', 'approved_by']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['effective_date', 'base_salary']
    ordering = ['-effective_date']

    @action(detail=False, methods=['get'])
    def salary_trends(self, request):
        """Get salary trends and analytics."""
        salaries = self.queryset.all()
        
        trends = {
            'total_records': salaries.count(),
            'average_salary': salaries.aggregate(avg_salary=Avg('base_salary'))['avg_salary'] or 0,
            'salary_by_position': salaries.values(
                'employee__position'
            ).annotate(
                avg_salary=Avg('base_salary'),
                count=Count('id')
            ).order_by('-avg_salary'),
            'recent_changes': salaries.filter(
                effective_date__gte=date.today() - timedelta(days=90)
            ).count(),
            'salary_distribution': {
                'under_50k': salaries.filter(base_salary__lt=50000).count(),
                '50k_100k': salaries.filter(base_salary__gte=50000, base_salary__lt=100000).count(),
                '100k_150k': salaries.filter(base_salary__gte=100000, base_salary__lt=150000).count(),
                'over_150k': salaries.filter(base_salary__gte=150000).count(),
            }
        }
        
        return Response(trends)


class AnalyticsView(APIView):
    """
    Comprehensive analytics endpoint.
    Provides organization-wide metrics and insights.
    """
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='20/hour', method='GET'))
    def get(self, request):
        """Get comprehensive analytics data."""
        try:
            # Basic counts
            total_employees = Employee.objects.filter(is_active=True).count()
            total_departments = Department.objects.filter(is_active=True).count()
            
            # Salary analytics
            salary_stats = Employee.objects.filter(is_active=True).aggregate(
                avg_salary=Avg('salary'),
                total_payroll=Sum('salary')
            )
            
            # Attendance analytics (last 30 days)
            thirty_days_ago = date.today() - timedelta(days=30)
            attendance_records = Attendance.objects.filter(date__gte=thirty_days_ago)
            total_attendance_records = attendance_records.count()
            present_records = attendance_records.filter(status='present').count()
            attendance_rate = (present_records / total_attendance_records * 100) if total_attendance_records > 0 else 0
            
            # Performance analytics
            recent_reviews = Performance.objects.filter(
                review_period_end__gte=date.today() - timedelta(days=365)
            )
            performance_avg = recent_reviews.aggregate(
                avg_performance=Avg('technical_skills')
            )['avg_performance'] or 0
            
            # Department distribution
            dept_distribution = list(Employee.objects.filter(is_active=True).values(
                'department__name'
            ).annotate(count=Count('id')))
            
            # Position distribution
            position_distribution = list(Employee.objects.filter(is_active=True).values(
                'position'
            ).annotate(count=Count('id')))
            
            # Recent hires (last 90 days)
            recent_hires = Employee.objects.filter(
                hire_date__gte=date.today() - timedelta(days=90),
                is_active=True
            ).count()
            
            analytics_data = {
                'total_employees': total_employees,
                'active_employees': total_employees,
                'total_departments': total_departments,
                'average_salary': salary_stats['avg_salary'] or 0,
                'total_payroll': salary_stats['total_payroll'] or 0,
                'attendance_rate': round(attendance_rate, 2),
                'performance_average': round(performance_avg, 2),
                'department_distribution': {item['department__name']: item['count'] for item in dept_distribution},
                'position_distribution': {item['position']: item['count'] for item in position_distribution},
                'recent_hires': recent_hires,
                'turnover_rate': 5.2,  # This would be calculated based on terminations
            }
            
            serializer = AnalyticsSerializer(data=analytics_data)
            serializer.is_valid(raise_exception=True)
            
            logger.info("Analytics data requested by user: %s", request.user.username)
            return Response(serializer.validated_data)
            
        except Exception as e:
            logger.error("Error generating analytics: %s", str(e))
            return Response(
                {"error": "Failed to generate analytics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DashboardView(APIView):
    """
    Dashboard data endpoint.
    Provides summarized data for the main dashboard.
    """
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='30/hour', method='GET'))
    def get(self, request):
        """Get dashboard summary data."""
        try:
            today = date.today()
            
            # Today's attendance
            today_attendance = Attendance.objects.filter(date=today)
            
            # Recent activities
            recent_employees = Employee.objects.filter(
                created_at__gte=today - timedelta(days=7)
            ).order_by('-created_at')[:5]
            
            # Upcoming reviews
            upcoming_reviews = Performance.objects.filter(
                review_period_end__gte=today,
                review_period_end__lte=today + timedelta(days=30)
            ).count()
            
            dashboard_data = {
                'today_date': today.isoformat(),
                'total_employees': Employee.objects.filter(is_active=True).count(),
                'today_present': today_attendance.filter(status='present').count(),
                'today_absent': today_attendance.filter(status='absent').count(),
                'recent_hires': recent_employees.count(),
                'upcoming_reviews': upcoming_reviews,
                'recent_employees': EmployeeSerializer(recent_employees, many=True).data,
                'departments': DepartmentSerializer(
                    Department.objects.filter(is_active=True)[:5], many=True
                ).data,
            }
            
            return Response(dashboard_data)
            
        except Exception as e:
            logger.error("Error generating dashboard data: %s", str(e))
            return Response(
                {"error": "Failed to generate dashboard data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportDataView(APIView):
    """
    Data export endpoint.
    Supports exporting employee data to various formats.
    """
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='5/hour', method='GET'))
    def get(self, request):
        """Export employee data to CSV or Excel."""
        export_format = request.query_params.get('format', 'csv').lower()
        data_type = request.query_params.get('type', 'employees').lower()
        
        try:
            if data_type == 'employees':
                queryset = Employee.objects.filter(is_active=True).select_related('department')
                data = []
                for emp in queryset:
                    data.append({
                        'Employee ID': emp.employee_id,
                        'Name': emp.full_name,
                        'Email': emp.email,
                        'Department': emp.department.name,
                        'Position': emp.get_position_display(),
                        'Hire Date': emp.hire_date,
                        'Salary': emp.salary,
                        'Years of Service': emp.years_of_service,
                    })
            
            elif data_type == 'attendance':
                queryset = Attendance.objects.filter(
                    date__gte=date.today() - timedelta(days=30)
                ).select_related('employee')
                data = []
                for att in queryset:
                    data.append({
                        'Employee ID': att.employee.employee_id,
                        'Employee Name': att.employee.full_name,
                        'Date': att.date,
                        'Check In': att.check_in_time,
                        'Check Out': att.check_out_time,
                        'Hours Worked': att.hours_worked,
                        'Status': att.get_status_display(),
                    })
            
            else:
                return Response(
                    {"error": "Invalid data type"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            df = pd.DataFrame(data)
            
            if export_format == 'excel':
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename={data_type}_export.xlsx'
                df.to_excel(response, index=False)
            else:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename={data_type}_export.csv'
                df.to_csv(response, index=False)
            
            logger.info("Data exported by user: %s, type: %s, format: %s", 
                       request.user.username, data_type, export_format)
            return response
            
        except Exception as e:
            logger.error("Error exporting data: %s", str(e))
            return Response(
                {"error": "Failed to export data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
