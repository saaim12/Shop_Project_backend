# Automobile Shop Backend

Complete Django REST framework backend for an automobile repair shop management system.

## Features
## not all implemented they will be implemented by time
- User Management (Customers, Mechanics, Managers)
- Vehicle Management
- Service Management
- Inventory Management (Parts)
- Order Management
- Appointment Management
- Billing & Invoicing
- JWT Authentication
- API Versioning (v1, v2)
- Comprehensive Error Handling
- Caching & Redis Support
- Celery Task Queue
- Docker Support

## Project Structure

```
automobile_backend/
├── apps/                    # Domain-specific applications
├── config/                  # Project settings
├── core/                    # Shared authentication, permissions, middleware
├── common/                  # Utilities and helpers
├── infrastructure/          # Database, cache, storage
├── api/                     # API versioning layer
├── services/                # Business logic
├── repositories/            # Data access layer
├── tests/                   # Test suite
├── scripts/                 # Development scripts
├── docs/                    # Documentation
└── manage.py
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd automobile_backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Seed database (optional):**
   ```bash
   python scripts/seed_data.py
   ```

8. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## API Documentation

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

## Endpoints

### Users
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/{id}/` - Get user details
- `PUT /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user

### Vehicles
- `GET /api/v1/vehicles/` - List all vehicles
- `POST /api/v1/vehicles/` - Create new vehicle
- `GET /api/v1/vehicles/{id}/` - Get vehicle details
- `PUT /api/v1/vehicles/{id}/` - Update vehicle
- `DELETE /api/v1/vehicles/{id}/` - Delete vehicle

### Services
- `GET /api/v1/services/` - List all services
- `POST /api/v1/services/` - Create new service
- `GET /api/v1/services/{id}/` - Get service details
- `PUT /api/v1/services/{id}/` - Update service
- `DELETE /api/v1/services/{id}/` - Delete service

### Orders
- `GET /api/v1/orders/` - List all orders
- `POST /api/v1/orders/` - Create new order
- `GET /api/v1/orders/{id}/` - Get order details
- `PUT /api/v1/orders/{id}/` - Update order
- `DELETE /api/v1/orders/{id}/` - Delete order

### Appointments
- `GET /api/v1/appointments/` - List all appointments
- `POST /api/v1/appointments/` - Create new appointment
- `GET /api/v1/appointments/{id}/` - Get appointment details
- `PUT /api/v1/appointments/{id}/` - Update appointment
- `DELETE /api/v1/appointments/{id}/` - Delete appointment

### Billing
- `GET /api/v1/billing/` - List all invoices
- `POST /api/v1/billing/` - Create new invoice
- `GET /api/v1/billing/{id}/` - Get invoice details
- `PUT /api/v1/billing/{id}/` - Update invoice
- `DELETE /api/v1/billing/{id}/` - Delete invoice

## Docker

Build and run with Docker Compose:

```bash
docker-compose up -d
```

Access the application at `http://localhost:8000`

## Testing

Run tests:

```bash
pytest              # Run all tests
pytest --cov       # With coverage
pytest tests/unit  # Unit tests only
```

## Requirements

- Python 3.9+
- Django 4.2+
- PostgreSQL (for production)
- Redis (for caching and Celery)

## Development

Activate debug toolbar by setting `DEBUG=True` in `.env` and accessing any page.

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## License

MIT License

## Support

For support, email support@automobileshop.com
