"""
Core views for authentication and system utilities.
Employee Management System - Core Views

This module contains authentication views and system utilities including:
- User registration and profile management
- Health check endpoint
- Password change functionality
"""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import connection
from django.conf import settings
from django.utils import timezone
from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer,
    ChangePasswordSerializer
)
import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    Allows new users to register for the system.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Handle user registration with logging."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"New user registered: {user.username}")
        return Response(
            {"message": "User created successfully", "user_id": user.id},
            status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile management endpoint.
    Allows authenticated users to view and update their profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the current user's profile."""
        return self.request.user


class ChangePasswordView(APIView):
    """
    Password change endpoint.
    Allows authenticated users to change their password.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handle password change request."""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"error": "Invalid old password"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            logger.info(f"Password changed for user: {user.username}")
            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring system status.
    Returns system health information including database connectivity.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Perform health checks and return system status.
        
        Returns:
            Response: JSON containing health status information
        """
        health_data = {
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "version": "1.0.0",
            "environment": getattr(settings, 'ENVIRONMENT', 'unknown'),
            "checks": {}
        }

        # Database connectivity check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_data["checks"]["database"] = {
                    "status": "healthy",
                    "message": "Database connection successful"
                }
        except Exception as e:
            health_data["status"] = "unhealthy"
            health_data["checks"]["database"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }

        # Determine overall status
        status_code = status.HTTP_200_OK
        if health_data["status"] == "unhealthy":
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(health_data, status=status_code)
