"""
Django management command to generate synthetic employee data.
Employee Data Generation & Visualization System - Data Generator

This command generates realistic employee data using Faker library including:
- Departments with managers and budgets
- Employees with comprehensive information
- Attendance records with realistic patterns
- Performance reviews with ratings
- Salary records with history

Usage: python manage.py generate_employee_data [--employees=5] [--days=30]
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker
import random
from datetime import date, timedelta
from decimal import Decimal

from employees.models import Department, Employee, Attendance, Performance, Salary


class Command(BaseCommand):
    """Management command to generate synthetic employee data."""
    
    help = 'Generate synthetic employee data for testing and development'

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--employees',
            type=int,
            default=5,
            help='Number of employees to create (default: 5)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of attendance data to generate (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new data'
        )

    def handle(self, *args, **options):
        """Main command handler."""
        self.fake = Faker()
        self.employees_count = options['employees']
        self.days_count = options['days']
        
        try:
            if options['clear']:
                self.clear_existing_data()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Starting data generation: {self.employees_count} employees, '
                    f'{self.days_count} days of data'
                )
            )
            
            # Generate data in sequence
            departments = self.create_departments()
            employees = self.create_employees(departments)
            self.create_attendance_records(employees)
            self.create_performance_reviews(employees)
            self.create_salary_records(employees)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully generated data for {len(employees)} employees '
                    f'across {len(departments)} departments'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Data generation failed: {str(e)}')

    def clear_existing_data(self):
        """Clear existing employee data."""
        self.stdout.write('Clearing existing data...')
        
        # Delete in reverse dependency order
        Salary.objects.all().delete()
        Performance.objects.all().delete()
        Attendance.objects.all().delete()
        Employee.objects.all().delete()
        Department.objects.all().delete()
        
        # Keep superuser, delete other users
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))

    def create_departments(self):
        """Create company departments."""
        self.stdout.write('Creating departments...')
        
        departments_data = [
            {
                'name': 'Engineering',
                'description': 'Software development and technical innovation',
                'budget': Decimal('2500000.00')
            },
            {
                'name': 'Marketing',
                'description': 'Brand promotion and customer acquisition',
                'budget': Decimal('1800000.00')
            },
            {
                'name': 'Sales',
                'description': 'Revenue generation and client relationships',
                'budget': Decimal('2200000.00')
            },
            {
                'name': 'Human Resources',
                'description': 'Employee management and organizational development',
                'budget': Decimal('1200000.00')
            },
            {
                'name': 'Finance',
                'description': 'Financial planning and accounting',
                'budget': Decimal('1500000.00')
            },
        ]
        
        departments = []
        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={
                    'description': dept_data['description'],
                    'budget': dept_data['budget'],
                    'is_active': True
                }
            )
            departments.append(department)
            
            if created:
                self.stdout.write(f'  Created department: {department.name}')
        
        return departments

    def create_employees(self, departments):
        """Create employees for each department."""
        self.stdout.write('Creating employees...')
        
        employees = []
        employee_counter = 1
        
        positions = ['intern', 'junior', 'senior', 'lead', 'manager', 'director']
        position_weights = [0.1, 0.3, 0.3, 0.15, 0.1, 0.05]  # Distribution weights
        
        for i in range(self.employees_count):
            # Create user account
            username = f'employee_{employee_counter:03d}'
            email = self.fake.email()
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='password123'  # Default password for testing
            )
            
            # Select department and position
            department = random.choice(departments)
            position = random.choices(positions, weights=position_weights)[0]
            
            # Generate salary based on position
            salary_ranges = {
                'intern': (40000, 55000),
                'junior': (60000, 85000),
                'senior': (90000, 130000),
                'lead': (120000, 160000),
                'manager': (140000, 190000),
                'director': (180000, 250000),
            }
            min_salary, max_salary = salary_ranges[position]
            salary = Decimal(str(random.randint(min_salary, max_salary)))
            
            # Create employee
            hire_date = self.fake.date_between(start_date='-5y', end_date='today')
            birth_date = self.fake.date_between(start_date='-65y', end_date='-22y')
            
            employee = Employee.objects.create(
                employee_id=f'EMP{employee_counter:03d}',
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=self.fake.phone_number()[:20],
                department=department,
                position=position,
                hire_date=hire_date,
                birth_date=birth_date,
                salary=salary,
                is_active=True
            )
            
            employees.append(employee)
            employee_counter += 1
            
            self.stdout.write(f'  Created employee: {employee.employee_id} - {employee.full_name}')
        
        # Assign managers to departments (select senior employees as managers)
        potential_managers = [emp for emp in employees if emp.position in ['lead', 'manager', 'director']]
        for department in departments:
            dept_employees = [emp for emp in employees if emp.department == department]
            dept_managers = [emp for emp in dept_employees if emp in potential_managers]
            
            if dept_managers:
                department.manager = random.choice(dept_managers)
                department.save()
                self.stdout.write(f'  Assigned manager: {department.manager.full_name} to {department.name}')
        
        return employees

    def create_attendance_records(self, employees):
        """Create attendance records for employees."""
        self.stdout.write('Creating attendance records...')
        
        end_date = date.today()
        start_date = end_date - timedelta(days=self.days_count)
        
        attendance_statuses = ['present', 'absent', 'late', 'half_day', 'sick_leave', 'vacation']
        status_weights = [0.75, 0.05, 0.1, 0.05, 0.03, 0.02]  # Realistic distribution
        
        records_created = 0
        for current_date in self.date_range(start_date, end_date):
            # Skip weekends for most employees
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                continue
                
            for employee in employees:
                # Some employees might work weekends occasionally
                if current_date.weekday() >= 5 and random.random() > 0.1:
                    continue
                
                status = random.choices(attendance_statuses, weights=status_weights)[0]
                
                # Generate realistic check-in/out times
                check_in_time = None
                check_out_time = None
                break_duration = 0
                
                if status in ['present', 'late', 'half_day']:
                    # Base check-in time around 9 AM
                    base_checkin = 9 * 60  # 9 AM in minutes
                    if status == 'late':
                        base_checkin += random.randint(15, 120)  # 15 minutes to 2 hours late
                    else:
                        base_checkin += random.randint(-30, 30)  # +/- 30 minutes variation
                    
                    check_in_hour = base_checkin // 60
                    check_in_minute = base_checkin % 60
                    check_in_time = f'{check_in_hour:02d}:{check_in_minute:02d}:00'
                    
                    # Check-out time (8-9 hours later)
                    if status == 'half_day':
                        work_minutes = random.randint(240, 300)  # 4-5 hours
                    else:
                        work_minutes = random.randint(480, 540)  # 8-9 hours
                    
                    checkout_minutes = base_checkin + work_minutes
                    checkout_hour = checkout_minutes // 60
                    checkout_minute = checkout_minutes % 60
                    check_out_time = f'{checkout_hour:02d}:{checkout_minute:02d}:00'
                    
                    # Break duration (30-90 minutes)
                    break_duration = random.randint(30, 90)
                
                # Create attendance record
                attendance = Attendance.objects.create(
                    employee=employee,
                    date=current_date,
                    check_in_time=check_in_time,
                    check_out_time=check_out_time,
                    break_duration=break_duration,
                    status=status,
                    notes=self.fake.sentence() if random.random() < 0.1 else ''
                )
                records_created += 1
        
        self.stdout.write(f'  Created {records_created} attendance records')

    def create_performance_reviews(self, employees):
        """Create performance review records."""
        self.stdout.write('Creating performance reviews...')
        
        reviews_created = 0
        potential_reviewers = [emp for emp in employees if emp.position in ['lead', 'manager', 'director']]
        
        for employee in employees:
            # Create 1-2 performance reviews per employee
            num_reviews = random.randint(1, 2)
            
            for i in range(num_reviews):
                # Review period (quarterly or semi-annual)
                months_ago = random.randint(3, 18)
                review_end = date.today() - timedelta(days=months_ago * 30)
                review_start = review_end - timedelta(days=90)  # 3-month review period
                
                # Select reviewer (preferably from same or related department)
                reviewer = None
                if potential_reviewers:
                    # Prefer reviewers from same department
                    same_dept_reviewers = [r for r in potential_reviewers if r.department == employee.department]
                    if same_dept_reviewers:
                        reviewer = random.choice(same_dept_reviewers)
                    else:
                        reviewer = random.choice(potential_reviewers)
                
                # Generate realistic ratings based on position and experience
                base_rating = 3  # Average performance
                if employee.position in ['senior', 'lead', 'manager']:
                    base_rating = 4  # Higher baseline for senior positions
                
                # Add some randomness
                rating_adjustment = random.uniform(-0.8, 1.2)
                
                technical_skills = max(1, min(5, round(base_rating + rating_adjustment + random.uniform(-0.5, 0.5))))
                communication = max(1, min(5, round(base_rating + rating_adjustment + random.uniform(-0.5, 0.5))))
                teamwork = max(1, min(5, round(base_rating + rating_adjustment + random.uniform(-0.5, 0.5))))
                leadership = max(1, min(5, round(base_rating + rating_adjustment + random.uniform(-0.5, 0.5))))
                
                goals_achieved = max(0, min(100, round(70 + rating_adjustment * 20 + random.randint(-20, 20))))
                
                performance = Performance.objects.create(
                    employee=employee,
                    review_period_start=review_start,
                    review_period_end=review_end,
                    reviewer=reviewer,
                    technical_skills=technical_skills,
                    communication=communication,
                    teamwork=teamwork,
                    leadership=leadership,
                    goals_achieved=goals_achieved,
                    feedback=self.fake.paragraph(nb_sentences=3)
                )
                reviews_created += 1
        
        self.stdout.write(f'  Created {reviews_created} performance reviews')

    def create_salary_records(self, employees):
        """Create salary history records."""
        self.stdout.write('Creating salary records...')
        
        records_created = 0
        potential_approvers = [emp for emp in employees if emp.position in ['manager', 'director']]
        
        for employee in employees:
            # Initial salary record (at hire date)
            initial_salary = Salary.objects.create(
                employee=employee,
                effective_date=employee.hire_date,
                base_salary=employee.salary,
                allowances=Decimal(str(random.randint(1000, 5000))),
                bonus=0,
                deductions=Decimal(str(random.randint(500, 2000))),
                salary_type='initial',
                reason='Initial salary upon hiring',
                approved_by=random.choice(potential_approvers) if potential_approvers else None
            )
            records_created += 1
            
            # Generate salary adjustments (1-3 over time)
            years_employed = (date.today() - employee.hire_date).days // 365
            if years_employed > 0:
                num_adjustments = min(years_employed, random.randint(0, 3))
                
                current_salary = employee.salary
                for i in range(num_adjustments):
                    # Salary adjustment date (spread over employment period)
                    days_since_hire = (date.today() - employee.hire_date).days
                    adjustment_days = random.randint(365, days_since_hire)
                    adjustment_date = employee.hire_date + timedelta(days=adjustment_days)
                    
                    # Salary increase (3-15%)
                    increase_percentage = random.uniform(0.03, 0.15)
                    new_salary = current_salary * Decimal(str(1 + increase_percentage))
                    current_salary = new_salary
                    
                    salary_types = ['annual_raise', 'promotion', 'performance_bonus', 'adjustment']
                    salary_type = random.choice(salary_types)
                    
                    salary_record = Salary.objects.create(
                        employee=employee,
                        effective_date=adjustment_date,
                        base_salary=new_salary,
                        allowances=Decimal(str(random.randint(1000, 6000))),
                        bonus=Decimal(str(random.randint(0, 10000))) if salary_type == 'performance_bonus' else 0,
                        deductions=Decimal(str(random.randint(500, 2500))),
                        salary_type=salary_type,
                        reason=f'{salary_type.replace("_", " ").title()} - {increase_percentage:.1%} increase',
                        approved_by=random.choice(potential_approvers) if potential_approvers else None
                    )
                    records_created += 1
                    
                # Update employee's current salary to the latest
                employee.salary = current_salary
                employee.save()
        
        self.stdout.write(f'  Created {records_created} salary records')

    def date_range(self, start_date, end_date):
        """Generate date range between start and end dates."""
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)
