# Employee Management System - Windows Setup Script
# PowerShell script for setting up the development environment on Windows

Write-Host "🚀 Employee Management System Setup" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📋 Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# Check if PostgreSQL is accessible
try {
    $pgTest = & pg_isready 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL not accessible"
    }
} catch {
    Write-Host "⚠️  PostgreSQL is not running. Please start PostgreSQL service." -ForegroundColor Red
    Write-Host "   Make sure PostgreSQL is installed and running on port 5432" -ForegroundColor Yellow
    exit 1
}

# Create database if it doesn't exist
Write-Host "🗄️  Setting up database..." -ForegroundColor Yellow
try {
    & createdb employee_db 2>$null
} catch {
    Write-Host "Database already exists or couldn't be created" -ForegroundColor Yellow
}

# Run migrations
Write-Host "🔄 Running database migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
Write-Host "👤 Creating superuser (optional)..." -ForegroundColor Yellow
$createSuperuser = Read-Host "Would you like to create a superuser? (y/n)"
if ($createSuperuser -eq "y") {
    python manage.py createsuperuser
}

# Generate sample data
Write-Host "📊 Generating sample data..." -ForegroundColor Yellow
python manage.py generate_employee_data --employees=5 --days=30

# Collect static files
Write-Host "📁 Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Starting development server..." -ForegroundColor Green
Write-Host "   API Documentation: http://localhost:8000/" -ForegroundColor Cyan
Write-Host "   Admin Panel: http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host "   Dashboard: http://localhost:8000/templates/dashboard.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start development server
python manage.py runserver
