"""
Django models for employee management system.
Employee Data Generation & Visualization System - Database Models

This module contains all database models including:
- Department: Company departments
- Employee: Core employee information
- Attendance: Employee attendance tracking
- Performance: Employee performance evaluations
- Salary: Employee salary and compensation data
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class Department(models.Model):
    """
    Department model representing company departments.
    
    Attributes:
        name: Department name
        description: Department description
        manager: Department manager (Employee reference)
        budget: Department annual budget
        created_at: Department creation timestamp
        is_active: Department status
    """
    name = models.CharField(max_length=100, unique=True, help_text="Department name")
    description = models.TextField(blank=True, help_text="Department description")
    manager = models.ForeignKey(
        'Employee', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='managed_departments',
        help_text="Department manager"
    )
    budget = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        help_text="Annual department budget"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Department status")

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name

    @property
    def employee_count(self):
        """Return the number of employees in this department."""
        return self.employees.filter(is_active=True).count()


class Employee(models.Model):
    """
    Employee model representing company employees.
    
    Attributes:
        employee_id: Unique employee identifier
        user: Associated Django user account
        first_name: Employee first name
        last_name: Employee last name
        email: Employee email address
        phone: Employee phone number
        department: Employee department
        position: Job position/title
        hire_date: Employee hire date
        salary: Current salary
        is_active: Employment status
    """
    POSITION_CHOICES = [
        ('intern', 'Intern'),
        ('junior', 'Junior Developer'),
        ('senior', 'Senior Developer'),
        ('lead', 'Team Lead'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('vp', 'Vice President'),
        ('ceo', 'CEO'),
    ]

    employee_id = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Unique employee identifier"
    )
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Associated user account"
    )
    first_name = models.CharField(max_length=50, help_text="Employee first name")
    last_name = models.CharField(max_length=50, help_text="Employee last name")
    email = models.EmailField(unique=True, help_text="Employee email address")
    phone = models.CharField(max_length=20, blank=True, help_text="Phone number")
    department = models.ForeignKey(
        Department, 
        on_delete=models.PROTECT,
        related_name='employees',
        help_text="Employee department"
    )
    position = models.CharField(
        max_length=20, 
        choices=POSITION_CHOICES,
        default='junior',
        help_text="Job position"
    )
    hire_date = models.DateField(help_text="Employee hire date")
    birth_date = models.DateField(null=True, blank=True, help_text="Date of birth")
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Current annual salary"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Employment status")

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        """Return the employee's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def years_of_service(self):
        """Calculate years of service."""
        return (timezone.now().date() - self.hire_date).days // 365


class Attendance(models.Model):
    """
    Attendance model for tracking employee attendance.
    
    Attributes:
        employee: Employee reference
        date: Attendance date
        check_in_time: Check-in timestamp
        check_out_time: Check-out timestamp
        break_duration: Total break time in minutes
        status: Attendance status
        notes: Additional notes
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('holiday', 'Holiday'),
        ('sick_leave', 'Sick Leave'),
        ('vacation', 'Vacation'),
    ]

    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="Employee reference"
    )
    date = models.DateField(help_text="Attendance date")
    check_in_time = models.TimeField(null=True, blank=True, help_text="Check-in time")
    check_out_time = models.TimeField(null=True, blank=True, help_text="Check-out time")
    break_duration = models.PositiveIntegerField(
        default=0, 
        help_text="Break duration in minutes"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='present',
        help_text="Attendance status"
    )
    notes = models.TextField(blank=True, help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'employee']
        unique_together = ['employee', 'date']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.status}"

    @property
    def hours_worked(self):
        """Calculate hours worked for the day."""
        if self.check_in_time and self.check_out_time:
            from datetime import datetime, timedelta
            check_in = datetime.combine(self.date, self.check_in_time)
            check_out = datetime.combine(self.date, self.check_out_time)
            worked = check_out - check_in - timedelta(minutes=self.break_duration)
            return worked.total_seconds() / 3600
        return 0


class Performance(models.Model):
    """
    Performance model for tracking employee performance evaluations.
    
    Attributes:
        employee: Employee reference
        review_period_start: Review period start date
        review_period_end: Review period end date
        reviewer: Manager who conducted the review
        technical_skills: Technical skills rating
        communication: Communication skills rating
        teamwork: Teamwork rating
        leadership: Leadership rating
        overall_rating: Overall performance rating
        goals_achieved: Goals achievement percentage
        feedback: Performance feedback
    """
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='performance_reviews',
        help_text="Employee being reviewed"
    )
    review_period_start = models.DateField(help_text="Review period start date")
    review_period_end = models.DateField(help_text="Review period end date")
    reviewer = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_reviews',
        help_text="Manager conducting the review"
    )
    technical_skills = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Technical skills rating (1-5)"
    )
    communication = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Communication skills rating (1-5)"
    )
    teamwork = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Teamwork rating (1-5)"
    )
    leadership = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Leadership rating (1-5)"
    )
    goals_achieved = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text="Goals achievement percentage"
    )
    feedback = models.TextField(help_text="Performance feedback and comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-review_period_end', 'employee']
        verbose_name = 'Performance Review'
        verbose_name_plural = 'Performance Reviews'

    def __str__(self):
        return f"{self.employee.full_name} - {self.review_period_end}"

    @property
    def overall_rating(self):
        """Calculate overall performance rating."""
        return round((self.technical_skills + self.communication + 
                     self.teamwork + self.leadership) / 4, 2)


class Salary(models.Model):
    """
    Salary model for tracking employee salary history and adjustments.
    
    Attributes:
        employee: Employee reference
        effective_date: Date when salary change takes effect
        base_salary: Base annual salary
        allowances: Additional allowances
        deductions: Salary deductions
        bonus: Performance bonus
        salary_type: Type of salary adjustment
        reason: Reason for salary change
        approved_by: Manager who approved the change
    """
    SALARY_TYPE_CHOICES = [
        ('initial', 'Initial Salary'),
        ('promotion', 'Promotion'),
        ('annual_raise', 'Annual Raise'),
        ('performance_bonus', 'Performance Bonus'),
        ('adjustment', 'Salary Adjustment'),
        ('correction', 'Salary Correction'),
    ]

    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='salary_history',
        help_text="Employee reference"
    )
    effective_date = models.DateField(help_text="Effective date of salary change")
    base_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Base annual salary"
    )
    allowances = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        help_text="Additional allowances"
    )
    deductions = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        help_text="Salary deductions"
    )
    bonus = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        help_text="Performance bonus"
    )
    salary_type = models.CharField(
        max_length=20, 
        choices=SALARY_TYPE_CHOICES,
        default='initial',
        help_text="Type of salary adjustment"
    )
    reason = models.TextField(blank=True, help_text="Reason for salary change")
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_salaries',
        help_text="Manager who approved the change"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-effective_date', 'employee']
        verbose_name = 'Salary Record'
        verbose_name_plural = 'Salary Records'

    def __str__(self):
        return f"{self.employee.full_name} - {self.effective_date} - ${self.total_salary}"

    @property
    def total_salary(self):
        """Calculate total salary including allowances and bonuses."""
        return self.base_salary + self.allowances + self.bonus - self.deductions
