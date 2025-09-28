"""
Tests for employees app models and functionality.
Employee Management System - Unit Tests

This module contains unit tests for the employees app including:
- Model functionality and properties
- Data validation
- Business logic
- Relationships between models
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta

from .models import Department, Employee, Attendance, Performance, Salary


class DepartmentModelTest(TestCase):
    """Test cases for Department model."""

    def setUp(self):
        """Set up test data."""
        self.department = Department.objects.create(
            name="Engineering",
            description="Software development team",
            budget=Decimal('1000000.00')
        )

    def test_department_creation(self):
        """Test department creation and string representation."""
        self.assertEqual(self.department.name, "Engineering")
        self.assertEqual(str(self.department), "Engineering")
        self.assertTrue(self.department.is_active)

    def test_employee_count_property(self):
        """Test employee_count property."""
        self.assertEqual(self.department.employee_count, 0)
        
        # Create an employee
        user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        Employee.objects.create(
            employee_id="EMP001",
            user=user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            department=self.department,
            position="junior",
            hire_date=date.today(),
            salary=Decimal('70000.00')
        )
        
        self.assertEqual(self.department.employee_count, 1)


class EmployeeModelTest(TestCase):
    """Test cases for Employee model."""

    def setUp(self):
        """Set up test data."""
        self.department = Department.objects.create(
            name="Engineering",
            budget=Decimal('1000000.00')
        )
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            department=self.department,
            position="junior",
            hire_date=date.today() - timedelta(days=365),  # 1 year ago
            salary=Decimal('70000.00')
        )

    def test_employee_creation(self):
        """Test employee creation and basic properties."""
        self.assertEqual(self.employee.employee_id, "EMP001")
        self.assertEqual(self.employee.first_name, "John")
        self.assertEqual(self.employee.last_name, "Doe")
        self.assertTrue(self.employee.is_active)

    def test_full_name_property(self):
        """Test full_name computed property."""
        self.assertEqual(self.employee.full_name, "John Doe")

    def test_years_of_service_property(self):
        """Test years_of_service computed property."""
        # Should be approximately 1 year
        self.assertEqual(self.employee.years_of_service, 1)

    def test_string_representation(self):
        """Test string representation."""
        expected = "EMP001 - John Doe"
        self.assertEqual(str(self.employee), expected)

    def test_unique_employee_id(self):
        """Test that employee_id must be unique."""
        with self.assertRaises(Exception):
            Employee.objects.create(
                employee_id="EMP001",  # Duplicate ID
                first_name="Jane",
                last_name="Smith",
                email="jane@example.com",
                department=self.department,
                position="senior",
                hire_date=date.today(),
                salary=Decimal('80000.00')
            )


class AttendanceModelTest(TestCase):
    """Test cases for Attendance model."""

    def setUp(self):
        """Set up test data."""
        self.department = Department.objects.create(
            name="Engineering",
            budget=Decimal('1000000.00')
        )
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            department=self.department,
            position="junior",
            hire_date=date.today(),
            salary=Decimal('70000.00')
        )

    def test_attendance_creation(self):
        """Test attendance record creation."""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in_time="09:00:00",
            check_out_time="17:00:00",
            break_duration=60,
            status="present"
        )
        
        self.assertEqual(attendance.employee, self.employee)
        self.assertEqual(attendance.status, "present")

    def test_hours_worked_calculation(self):
        """Test hours_worked property calculation."""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in_time="09:00:00",
            check_out_time="17:00:00",
            break_duration=60,  # 1 hour break
            status="present"
        )
        
        # 8 hours work - 1 hour break = 7 hours
        self.assertEqual(attendance.hours_worked, 7.0)

    def test_unique_employee_date(self):
        """Test that employee can only have one attendance record per date."""
        Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            status="present"
        )
        
        with self.assertRaises(Exception):
            Attendance.objects.create(
                employee=self.employee,
                date=date.today(),  # Same date
                status="late"
            )


class PerformanceModelTest(TestCase):
    """Test cases for Performance model."""

    def setUp(self):
        """Set up test data."""
        self.department = Department.objects.create(
            name="Engineering",
            budget=Decimal('1000000.00')
        )
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            department=self.department,
            position="junior",
            hire_date=date.today(),
            salary=Decimal('70000.00')
        )
        self.reviewer = Employee.objects.create(
            employee_id="EMP002",
            first_name="Jane",
            last_name="Manager",
            email="jane@example.com",
            department=self.department,
            position="manager",
            hire_date=date.today(),
            salary=Decimal('90000.00')
        )

    def test_performance_creation(self):
        """Test performance review creation."""
        performance = Performance.objects.create(
            employee=self.employee,
            review_period_start=date.today() - timedelta(days=90),
            review_period_end=date.today(),
            reviewer=self.reviewer,
            technical_skills=4,
            communication=3,
            teamwork=4,
            leadership=3,
            goals_achieved=85,
            feedback="Good performance overall"
        )
        
        self.assertEqual(performance.employee, self.employee)
        self.assertEqual(performance.reviewer, self.reviewer)

    def test_overall_rating_calculation(self):
        """Test overall_rating property calculation."""
        performance = Performance.objects.create(
            employee=self.employee,
            review_period_start=date.today() - timedelta(days=90),
            review_period_end=date.today(),
            reviewer=self.reviewer,
            technical_skills=4,
            communication=3,
            teamwork=4,
            leadership=3,
            goals_achieved=85,
            feedback="Good performance"
        )
        
        # (4 + 3 + 4 + 3) / 4 = 3.5
        self.assertEqual(performance.overall_rating, 3.5)


class SalaryModelTest(TestCase):
    """Test cases for Salary model."""

    def setUp(self):
        """Set up test data."""
        self.department = Department.objects.create(
            name="Engineering",
            budget=Decimal('1000000.00')
        )
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            department=self.department,
            position="junior",
            hire_date=date.today(),
            salary=Decimal('70000.00')
        )

    def test_salary_creation(self):
        """Test salary record creation."""
        salary = Salary.objects.create(
            employee=self.employee,
            effective_date=date.today(),
            base_salary=Decimal('70000.00'),
            allowances=Decimal('5000.00'),
            bonus=Decimal('10000.00'),
            deductions=Decimal('2000.00'),
            salary_type="initial",
            reason="Initial salary"
        )
        
        self.assertEqual(salary.employee, self.employee)
        self.assertEqual(salary.base_salary, Decimal('70000.00'))

    def test_total_salary_calculation(self):
        """Test total_salary property calculation."""
        salary = Salary.objects.create(
            employee=self.employee,
            effective_date=date.today(),
            base_salary=Decimal('70000.00'),
            allowances=Decimal('5000.00'),
            bonus=Decimal('10000.00'),
            deductions=Decimal('2000.00'),
            salary_type="initial"
        )
        
        # 70000 + 5000 + 10000 - 2000 = 83000
        self.assertEqual(salary.total_salary, Decimal('83000.00'))

    def test_string_representation(self):
        """Test string representation."""
        salary = Salary.objects.create(
            employee=self.employee,
            effective_date=date.today(),
            base_salary=Decimal('70000.00'),
            salary_type="initial"
        )
        
        expected = f"John Doe - {date.today()} - ${salary.total_salary}"
        self.assertEqual(str(salary), expected)
