# Employee Management System

A comprehensive Django REST API application for employee data generation, management, and visualization built for the 3-hour development challenge.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd glynac-assignment
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb employee_db
   
   # Copy environment file
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Generate sample data**
   ```bash
   python manage.py generate_employee_data --employees=5 --days=30
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - API Documentation (Swagger): http://localhost:8000/
   - Admin Interface: http://localhost:8000/admin/
   - Dashboard: http://localhost:8000/templates/dashboard.html

## 🐳 Docker Setup (Alternative)

```bash
# Start all services
docker-compose up -d

# Access the application
# API: http://localhost:8000/
# Database: localhost:5432
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `POST /api/auth/register/` - User registration

### Core Resources
- `GET/POST /api/v1/employees/` - List/Create employees
- `GET/PUT/PATCH/DELETE /api/v1/employees/{id}/` - Employee details
- `GET/POST /api/v1/departments/` - List/Create departments
- `GET/POST /api/v1/attendance/` - Attendance records
- `GET/POST /api/v1/performance/` - Performance reviews
- `GET/POST /api/v1/salary/` - Salary records

### Analytics & Reports
- `GET /api/v1/analytics/` - Organization analytics
- `GET /api/v1/dashboard/` - Dashboard data
- `GET /api/v1/export/?format=csv&type=employees` - Export data

### Health Check
- `GET /health/` - System health status

## 🔧 Features Implemented

### ✅ Core Features (High Priority)
- **Database Models**: 5 comprehensive models (Employee, Department, Attendance, Performance, Salary)
- **REST API**: Full CRUD operations with DRF
- **PostgreSQL Integration**: Production-ready database setup
- **Data Generation**: Faker-based synthetic data creation
- **Authentication**: JWT-based API authentication
- **API Documentation**: Swagger UI with drf-yasg

### ✅ Advanced Features (Medium Priority)
- **Rate Limiting**: API throttling (100/hour for anonymous, 1000/hour for authenticated)
- **Filtering & Pagination**: Advanced query capabilities
- **Data Export**: CSV/Excel export functionality
- **Analytics Dashboard**: Interactive charts and visualizations
- **Admin Interface**: Enhanced Django admin with inline editing

### ✅ Bonus Features (Low Priority)
- **Docker Support**: Full containerization with docker-compose
- **Environment Configuration**: .env file management
- **Logging**: Comprehensive application logging
- **Health Checks**: System monitoring endpoints
- **Data Visualization**: Chart.js and Plotly integration

## 🏗️ Architecture

### Project Structure
```
employee_management/
├── employee_management/    # Django project settings
├── employees/             # Core business logic models
├── api/                   # REST API endpoints
├── core/                  # Authentication & utilities
├── templates/            # HTML templates
├── static/               # Static files
├── logs/                 # Application logs
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Container orchestration
└── README.md            # This file
```

### Database Schema
- **Department**: Company departments with budgets and managers
- **Employee**: Core employee information with relationships
- **Attendance**: Daily attendance tracking with hours worked
- **Performance**: Quarterly/annual performance reviews
- **Salary**: Salary history and adjustments

### API Design
- RESTful endpoints following Django REST Framework conventions
- JWT authentication for secure access
- Consistent error handling and response formats
- Comprehensive filtering and pagination
- Rate limiting for API protection

## 🔍 Sample Data

The system generates realistic sample data including:
- **5 Departments**: Engineering, Marketing, Sales, HR, Finance
- **5+ Employees**: With varied positions from Intern to Director
- **30 Days** of attendance records with realistic patterns
- **Performance Reviews**: Quarterly evaluations with ratings
- **Salary History**: Initial salaries plus adjustments over time

## 📊 Analytics Features

### Dashboard Metrics
- Total employees count
- Daily attendance rates
- Average salary calculations
- Performance score averages
- Department distribution
- Position hierarchy breakdown

### Visualizations
- **Pie Charts**: Department and position distributions
- **Bar Charts**: Salary range distributions
- **Gauge Charts**: Attendance rate indicators
- **Time Series**: Performance trends over time

## 🔐 Security Features

- JWT-based authentication
- Rate limiting and throttling
- CORS configuration
- Input validation and sanitization
- SQL injection protection via Django ORM
- XSS protection headers

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📝 API Usage Examples

### Authentication
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123", "email": "test@example.com"}'

# Get token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### Employee Operations
```bash
# List employees
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/employees/

# Get employee details
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/employees/1/

# Filter employees by department
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/employees/?department=1"
```

### Analytics
```bash
# Get analytics data
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/analytics/

# Export employee data
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/export/?format=csv&type=employees"
```

## 🚀 Deployment

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/employee_db
DB_NAME=employee_db
DB_USER=postgres
DB_PASSWORD=your_password

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# JWT
JWT_SECRET_KEY=your-jwt-secret
```

### Production Deployment
1. Set `DEBUG=False` in environment
2. Configure proper `ALLOWED_HOSTS`
3. Set up SSL/HTTPS
4. Use production database
5. Configure proper logging
6. Set up monitoring

## 🛠️ Development

### Management Commands
```bash
# Generate test data
python manage.py generate_employee_data --employees=10 --days=60

# Clear existing data
python manage.py generate_employee_data --clear

# Create superuser
python manage.py createsuperuser
```

### Code Quality
- Follow PEP 8 style guidelines
- Comprehensive docstrings
- Type hints where applicable
- Modular architecture
- DRY principles

## 📈 Performance Considerations

- Database query optimization with select_related/prefetch_related
- API pagination for large datasets
- Rate limiting to prevent abuse
- Efficient serializers
- Proper indexing on database fields
- Caching strategies for analytics data

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

This project is developed for educational purposes as part of a technical challenge.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Verify database credentials in `.env`
   - Check database exists

2. **Migration Issues**
   - Delete migration files and recreate: `python manage.py makemigrations`
   - Reset database if needed

3. **Authentication Issues**
   - Verify JWT token is valid
   - Check token expiration
   - Ensure proper Authorization header format

4. **Docker Issues**
   - Ensure Docker is running
   - Check port conflicts
   - Verify environment variables

## 📞 Support

For technical issues or questions, please refer to the code documentation or create an issue in the repository.

---

**Built with Django REST Framework | PostgreSQL | Docker | Chart.js | Plotly**