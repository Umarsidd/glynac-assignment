#!/bin/bash

# Employee Management System - Setup Script
# This script sets up the development environment and runs the application

echo "🚀 Employee Management System Setup"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if PostgreSQL is running
if ! pg_isready >/dev/null 2>&1; then
    echo "⚠️  PostgreSQL is not running. Please start PostgreSQL service."
    echo "   For macOS with Homebrew: brew services start postgresql"
    echo "   For Ubuntu: sudo service postgresql start"
    exit 1
fi

# Create database if it doesn't exist
echo "🗄️  Setting up database..."
createdb employee_db 2>/dev/null || echo "Database already exists"

# Run migrations
echo "🔄 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
echo "👤 Creating superuser (optional)..."
echo "Would you like to create a superuser? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

# Generate sample data
echo "📊 Generating sample data..."
python manage.py generate_employee_data --employees=5 --days=30

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup complete!"
echo ""
echo "🌐 Starting development server..."
echo "   API Documentation: http://localhost:8000/"
echo "   Admin Panel: http://localhost:8000/admin/"
echo "   Dashboard: http://localhost:8000/templates/dashboard.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start development server
python manage.py runserver
