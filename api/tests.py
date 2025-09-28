"""
Tests for API endpoints and functionality.
Employee Management System - API Tests

This module contains tests for the REST API endpoints including:
- Authentication and permissions
- CRUD operations
- Custom endpoints
- Data validation
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from datetime import date

from employees.models import Department, Employee, Attendance, Performance, Salary


class AuthenticationTest(APITestCase):
    """Test authentication functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_registration(self):
        """Test user registration endpoint."""
        url = reverse('core:user_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_jwt_token_obtain(self):
        """Test JWT token obtaining."""
        url = reverse('core:token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without authentication."""
        url = reverse('api:employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('api:employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DepartmentAPITest(APITestCase):
    """Test Department API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.department = Department.objects.create(
            name="Engineering",
            description="Software development team",
            budget=Decimal('1000000.00')
        )

    def test_department_list(self):
        """Test department list endpoint."""
        url = reverse('api:department-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_department_create(self):
        """Test department creation via API."""
        url = reverse('api:department-list')
        data = {
            'name': 'Marketing',
            'description': 'Marketing and promotion',
            'budget': '500000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Department.objects.filter(name='Marketing').exists())

    def test_department_detail(self):
        """Test department detail endpoint."""
        url = reverse('api:department-detail', kwargs={'pk': self.department.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Engineering')

    def test_department_update(self):
        """Test department update via API."""
        url = reverse('api:department-detail', kwargs={'pk': self.department.pk})
        data = {
            'name': 'Software Engineering',
            'description': 'Advanced software development',
            'budget': '1200000.00'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.department.refresh_from_db()
        self.assertEqual(self.department.name, 'Software Engineering')

    def test_department_delete(self):
        """Test department deletion via API."""
        url = reverse('api:department-detail', kwargs={'pk': self.department.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Department.objects.filter(pk=self.department.pk).exists())


class EmployeeAPITest(APITestCase):
    """Test Employee API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.department = Department.objects.create(
            name="Engineering",
            budget=Decimal('1000000.00')
        )
        
        self.employee_user = User.objects.create_user('emp001', 'emp@example.com', 'pass')
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            user=self.employee_user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            department=self.department,
            position="junior",
            hire_date=date.today(),
            salary=Decimal('70000.00')
        )

    def test_employee_list(self):
        """Test employee list endpoint."""
        url = reverse('api:employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_employee_create(self):
        """Test employee creation via API."""
        url = reverse('api:employee-list')
        data = {
            'employee_id': 'EMP002',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'department': self.department.pk,
            'position': 'senior',
            'hire_date': date.today().isoformat(),
            'salary': '85000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Employee.objects.filter(employee_id='EMP002').exists())

    def test_employee_detail(self):
        """Test employee detail endpoint."""
        url = reverse('api:employee-detail', kwargs={'pk': self.employee.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_id'], 'EMP001')
        self.assertEqual(response.data['full_name'], 'John Doe')

    def test_employee_filter_by_department(self):
        """Test filtering employees by department."""
        url = reverse('api:employee-list')
        response = self.client.get(url, {'department': self.department.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_employee_search(self):
        """Test searching employees."""
        url = reverse('api:employee-list')
        response = self.client.get(url, {'search': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class AnalyticsAPITest(APITestCase):
    """Test Analytics API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create test data
        self.department = Department.objects.create(
            name="Engineering",
            budget=Decimal('1000000.00')
        )
        
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            department=self.department,
            position="junior",
            hire_date=date.today(),
            salary=Decimal('70000.00')
        )

    def test_analytics_endpoint(self):
        """Test analytics endpoint."""
        url = reverse('api:analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check required fields
        required_fields = [
            'total_employees', 'active_employees', 'total_departments',
            'average_salary', 'attendance_rate', 'performance_average'
        ]
        for field in required_fields:
            self.assertIn(field, response.data)

    def test_dashboard_endpoint(self):
        """Test dashboard endpoint."""
        url = reverse('api:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check required fields
        required_fields = [
            'today_date', 'total_employees', 'today_present', 'today_absent'
        ]
        for field in required_fields:
            self.assertIn(field, response.data)

    def test_export_endpoint(self):
        """Test data export endpoint."""
        url = reverse('api:export_data')
        response = self.client.get(url, {'format': 'csv', 'type': 'employees'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')


class HealthCheckTest(APITestCase):
    """Test health check functionality."""

    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        url = reverse('health:health_check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('checks', response.data)
