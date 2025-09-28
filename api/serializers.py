"""
Serializers for API endpoints.
Employee Management System - API Serializers

This module contains all DRF serializers for API endpoints including:
- Model serializers for CRUD operations
- Custom serializers for analytics and reporting
- Nested serializers for related data
"""

from rest_framework import serializers
from employees.models import Department, Employee, Attendance, Performance, Salary
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model.
    Includes employee count and manager details.
    """
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    employee_count = serializers.ReadOnlyField()

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'description', 'manager', 'manager_name', 
            'budget', 'employee_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'employee_count']


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.
    Includes computed fields and related data.
    """
    full_name = serializers.ReadOnlyField()
    years_of_service = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'user', 'user_details', 'first_name', 'last_name', 
            'full_name', 'email', 'phone', 'department', 'department_name', 
            'position', 'hire_date', 'birth_date', 'salary', 'years_of_service',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'full_name', 'years_of_service']

    def validate_employee_id(self, value):
        """Ensure employee ID is unique."""
        if self.instance and self.instance.employee_id == value:
            return value
        if Employee.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID already exists.")
        return value


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model.
    Includes computed hours worked and employee details.
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    hours_worked = serializers.ReadOnlyField()

    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'date', 
            'check_in_time', 'check_out_time', 'break_duration', 'hours_worked',
            'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'hours_worked']

    def validate(self, data):
        """Validate attendance data."""
        if data.get('check_out_time') and data.get('check_in_time'):
            if data['check_out_time'] <= data['check_in_time']:
                raise serializers.ValidationError(
                    "Check-out time must be after check-in time."
                )
        return data


class PerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Performance model.
    Includes computed overall rating and employee/reviewer details.
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.full_name', read_only=True)
    overall_rating = serializers.ReadOnlyField()

    class Meta:
        model = Performance
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 
            'review_period_start', 'review_period_end', 
            'reviewer', 'reviewer_name', 'technical_skills', 'communication',
            'teamwork', 'leadership', 'overall_rating', 'goals_achieved',
            'feedback', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'overall_rating']

    def validate(self, data):
        """Validate performance review data."""
        if data['review_period_end'] <= data['review_period_start']:
            raise serializers.ValidationError(
                "Review period end must be after start date."
            )
        return data


class SalarySerializer(serializers.ModelSerializer):
    """
    Serializer for Salary model.
    Includes computed total salary and employee/approver details.
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    total_salary = serializers.ReadOnlyField()

    class Meta:
        model = Salary
        fields = [
            'id', 'employee', 'employee_name', 'employee_id',
            'effective_date', 'base_salary', 'allowances', 'deductions',
            'bonus', 'total_salary', 'salary_type', 'reason',
            'approved_by', 'approved_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_salary']


class EmployeeDetailSerializer(EmployeeSerializer):
    """
    Detailed Employee serializer with related data.
    Includes recent attendance, performance, and salary information.
    """
    recent_attendance = serializers.SerializerMethodField()
    latest_performance = serializers.SerializerMethodField()
    current_salary_details = serializers.SerializerMethodField()

    class Meta(EmployeeSerializer.Meta):
        fields = EmployeeSerializer.Meta.fields + [
            'recent_attendance', 'latest_performance', 'current_salary_details'
        ]

    def get_recent_attendance(self, obj):
        """Get recent attendance records (last 7 days)."""
        from datetime import date, timedelta
        recent_date = date.today() - timedelta(days=7)
        attendance = obj.attendance_records.filter(date__gte=recent_date).order_by('-date')[:7]
        return AttendanceSerializer(attendance, many=True).data

    def get_latest_performance(self, obj):
        """Get latest performance review."""
        performance = obj.performance_reviews.order_by('-review_period_end').first()
        if performance:
            return PerformanceSerializer(performance).data
        return None

    def get_current_salary_details(self, obj):
        """Get current salary details."""
        salary = obj.salary_history.order_by('-effective_date').first()
        if salary:
            return SalarySerializer(salary).data
        return None


class AnalyticsSerializer(serializers.Serializer):
    """
    Serializer for analytics data.
    Provides structure for dashboard and reporting data.
    """
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    average_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    attendance_rate = serializers.FloatField()
    performance_average = serializers.FloatField()
    department_distribution = serializers.DictField()
    position_distribution = serializers.DictField()
    recent_hires = serializers.IntegerField()
    turnover_rate = serializers.FloatField()
