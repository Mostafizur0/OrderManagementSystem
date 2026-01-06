# FastAPI Users Service (FastAPI folder structures, prometheus, grafana, docker)

A FastAPI-based REST API service for managing users with full CRUD operations, comprehensive logging, exception handling, and Prometheus metrics.

## Features

- **CRUD Operations**: Create, Read, Update, Delete users
- **Database Integration**: SQLAlchemy with PostgreSQL
- **Comprehensive Logging**: Request/response logging with file output
- **Exception Handling**: Custom exceptions with proper HTTP status codes
- **API Documentation**: Auto-generated Swagger/OpenAPI docs
- **Health Check**: Service health monitoring endpoint
- **CORS Support**: Cross-origin resource sharing enabled
- **Prometheus Metrics**: Request counts, durations, and active requests monitoring

## Project Structure

```
fastapi-users-service/
├── app/
│   ├── core/
│   │   └── settings.py          # Application settings
│   ├── crud/
│   │   ├── __init__.py
│   │   └── user.py              # User CRUD operations
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── custom_exceptions.py # Custom exception classes
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── logging_middleware.py # Request/response logging
│   │   └── metrics_middleware.py # Prometheus metrics
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py              # SQLAlchemy base model
│   │   └── users.py             # User model
│   ├── routes/
│   │   ├── __init__.py
│   │   └── users.py             # User API routes
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py              # Pydantic schemas
│   └── utils/
│       ├── __init__.py
│       └── logger.py            # Logging utilities
├── alembic/                     # Database migrations
├── logs/                        # Application logs
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Setup Instructions

### 1. Environment Setup

Create a `.env` file in the root directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_users_db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Make sure you have PostgreSQL running and create a database:

```sql
CREATE DATABASE fastapi_users_db;
```

### 4. Run Migrations (Optional)

If you want to use Alembic for database migrations:

```bash
alembic upgrade head
```

### 5. Start the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Base URLs
- **API Base**: `http://localhost:8000/api/v1`
- **Documentation**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`
- **Metrics**: `http://localhost:8000/metrics`

### User Endpoints

#### Create User
```http
POST /api/v1/users/
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
}
```

#### Get All Users
```http
GET /api/v1/users/?skip=0&limit=100
```

#### Get User by ID
```http
GET /api/v1/users/{user_id}
```

#### Update User
```http
PUT /api/v1/users/{user_id}
Content-Type: application/json

{
    "name": "John Updated",
    "email": "john.updated@example.com"
}
```

#### Delete User
```http
DELETE /api/v1/users/{user_id}
```

## Monitoring & Metrics

### Prometheus Metrics

The application exposes Prometheus metrics at `/metrics` endpoint:

- **http_requests_total**: Total number of HTTP requests by method, endpoint, and status
- **http_request_duration_seconds**: Request duration histogram by method and endpoint
- **http_active_requests_total**: Number of currently active requests

### Example Metrics Output

```
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health",status="200"} 5

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.1"} 5

# HELP http_requests_active Number of active HTTP requests
# TYPE http_requests_active counter
http_requests_active 0
```

## Logging

The application includes comprehensive logging:

- **Request/Response Logging**: All HTTP requests and responses are logged
- **Application Logs**: CRUD operations and business logic logging
- **Error Logging**: Exceptions and errors are logged with details
- **File Output**: Logs are saved to `logs/app.log`

## Exception Handling

The application includes custom exceptions:

- `UserNotFoundException`: When a user is not found (404)
- `UserAlreadyExistsException`: When trying to create a duplicate user (409)
- `DatabaseException`: Database operation failures (500)
- `ValidationException`: Input validation errors (422)

## Development

### Adding New Models

1. Create a new model in `app/models/`
2. Create corresponding schemas in `app/schemas/`
3. Create CRUD operations in `app/crud/`
4. Create API routes in `app/routes/`
5. Include the router in `main.py`

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Docker Support

Build and run with Docker:

```bash
# Build image
docker build -t fastapi-users-service .

# Run container
docker run -p 8000:8000 --env-file .env fastapi-users-service
```

## Production Considerations

1. **Environment Variables**: Use proper environment variables for sensitive data
2. **CORS**: Configure CORS origins properly for production
3. **Database**: Use connection pooling and proper database configuration
4. **Logging**: Configure log rotation and monitoring
5. **Security**: Add authentication and authorization
6. **Rate Limiting**: Implement rate limiting for API endpoints
7. **Monitoring**: Set up Prometheus and Grafana for metrics visualization

## License

This project is licensed under the MIT License.
