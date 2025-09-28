"""
Serializers for core authentication functionality.
Employee Management System - Core Serializers

This module contains serializers for authentication and user management including:
- User registration
- User profile management
- Password change functionality
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles new user account creation with password confirmation.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Confirm your password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """Validate password confirmation matches."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        """Create new user with encrypted password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile management.
    Allows users to view and update their profile information.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change functionality.
    Handles old password verification and new password validation.
    """
    old_password = serializers.CharField(
        required=True,
        help_text="Current password"
    )
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        validators=[validate_password],
        help_text="New password (min 8 characters)"
    )
    new_password_confirm = serializers.CharField(
        required=True,
        help_text="Confirm new password"
    )

    def validate(self, attrs):
        """Validate new password confirmation matches."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
