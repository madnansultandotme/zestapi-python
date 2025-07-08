# ZestAPI User Guide

A comprehensive guide to building modern REST APIs with ZestAPI framework.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [Application Structure](#application-structure)
6. [Routing](#routing)
7. [Request & Response Handling](#request-response-handling)
8. [Authentication & Security](#authentication-security)
9. [Middleware](#middleware)
10. [Error Handling](#error-handling)
11. [Rate Limiting](#rate-limiting)
12. [WebSocket Support](#websocket-support)
13. [Plugin System](#plugin-system)
14. [Configuration](#configuration)
15. [Deployment](#deployment)
16. [Best Practices](#best-practices)
17. [Examples](#examples)

## Introduction

ZestAPI is a modern, ASGI-compatible Python framework for building high-performance REST APIs. It combines the best features of Flask and FastAPI while providing a clean, intuitive API for rapid development.

### Key Features

- **Auto-routing**: Automatic route discovery from directory structure
- **Built-in JWT Authentication**: Secure authentication with JWT tokens
- **Rate Limiting**: Configurable rate limiting with multiple time windows
- **Plugin System**: Extensible architecture with custom middleware
- **High Performance**: Uses orjson for fast JSON serialization
- **WebSocket Support**: Real-time communication capabilities
- **Comprehensive Error Handling**: Production-ready error management
- **Type Safety**: Full type hint support with mypy compatibility

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Install ZestAPI

```bash
pip install zestapi
```

### Development Installation

```bash
git clone https://github.com/madnansultandotme/zestapi-python.git
cd zestapi-python
pip install -e .
```

## Quick Start

### 1. Create Your First API

```python
from zestapi import ZestAPI, route, ORJSONResponse

# Create ZestAPI instance
app_instance = ZestAPI()

# Define routes using decorators
@route("/")
async def homepage(request):
    return ORJSONResponse({
        "message": "Welcome to ZestAPI!",
        "version": "1.0.0"
    })

@route("/users", methods=["GET"])
async def get_users(request):
    return ORJSONResponse({
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    })

@route("/users", methods=["POST"])
async def create_user(request):
    data = await request.json()
    return ORJSONResponse({
        "message": "User created",
        "data": data
    }, status_code=201)

# Get the ASGI app
app = app_instance.app

if __name__ == "__main__":
    app_instance.run()
```

### 2. Run Your Application

```bash
python main.py
```

Your API will be available at `http://localhost:8000`

## Core Concepts

### ZestAPI Application

The main entry point for your application is the `ZestAPI` class:

```python
from zestapi import ZestAPI, Settings

# Basic initialization
app_instance = ZestAPI()

# With custom settings
settings = Settings()
settings.debug = True
settings.port = 9000
app_instance = ZestAPI(settings=settings)
```

### Route Decorators

ZestAPI provides decorators for easy route definition:

```python
from zestapi import route, websocket_route

# HTTP routes
@route("/path", methods=["GET", "POST"])
async def handler(request):
    return ORJSONResponse({"data": "response"})

# WebSocket routes
@websocket_route("/ws")
async def websocket_handler(websocket):
    await websocket.accept()
    await websocket.send_text("Hello!")
```

### Response Types

ZestAPI provides optimized response types:

```python
from zestapi import ORJSONResponse

# High-performance JSON response
return ORJSONResponse({
    "message": "Success",
    "data": {"key": "value"}
}, status_code=200)
```

## Application Structure

### Recommended Project Structure

```
my-api/
├── main.py                 # Application entry point
├── .env                    # Environment variables
├── requirements.txt        # Dependencies
├── app/
│   ├── routes/            # Route files (auto-discovered)
│   │   ├── users.py
│   │   ├── products.py
│   │   └── auth.py
│   ├── plugins/           # Custom plugins
│   │   └── example_plugin.py
│   ├── models/            # Data models
│   │   └── user.py
│   └── utils/             # Utility functions
│       └── helpers.py
└── tests/                 # Test files
    └── test_api.py
```

### Auto-Discovery

ZestAPI automatically discovers routes from the `app/routes/` directory:

```python
# app/routes/users.py
from zestapi import route, ORJSONResponse

@route("/users", methods=["GET"])
async def get_users(request):
    return ORJSONResponse({"users": []})

@route("/users/{user_id}", methods=["GET"])
async def get_user(request):
    user_id = request.path_params["user_id"]
    return ORJSONResponse({"user_id": user_id})
```

## Routing

### HTTP Routes

```python
from zestapi import route, ORJSONResponse

# GET route
@route("/users", methods=["GET"])
async def get_users(request):
    return ORJSONResponse({"users": []})

# POST route with JSON body
@route("/users", methods=["POST"])
async def create_user(request):
    data = await request.json()
    return ORJSONResponse({"created": data}, status_code=201)

# PUT route with path parameters
@route("/users/{user_id}", methods=["PUT"])
async def update_user(request):
    user_id = request.path_params["user_id"]
    data = await request.json()
    return ORJSONResponse({"updated": user_id, "data": data})

# DELETE route
@route("/users/{user_id}", methods=["DELETE"])
async def delete_user(request):
    user_id = request.path_params["user_id"]
    return ORJSONResponse({"deleted": user_id})
```

### WebSocket Routes

```python
from zestapi import websocket_route
import json

@websocket_route("/ws")
async def websocket_handler(websocket):
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_text()
            data = json.loads(message)
            
            # Send response
            response = {"echo": data}
            await websocket.send_text(json.dumps(response))
            
    except Exception as e:
        await websocket.close()
```

### Path Parameters

```python
@route("/users/{user_id}/posts/{post_id}")
async def get_user_post(request):
    user_id = request.path_params["user_id"]
    post_id = request.path_params["post_id"]
    return ORJSONResponse({
        "user_id": user_id,
        "post_id": post_id
    })
```

### Query Parameters

```python
@route("/search")
async def search(request):
    query = request.query_params.get("q", "")
    page = int(request.query_params.get("page", "1"))
    limit = int(request.query_params.get("limit", "10"))
    
    return ORJSONResponse({
        "query": query,
        "page": page,
        "limit": limit
    })
```

## Request & Response Handling

### Request Object

The `request` object provides access to all request data:

```python
@route("/example", methods=["POST"])
async def example(request):
    # Headers
    content_type = request.headers.get("content-type")
    user_agent = request.headers.get("user-agent")
    
    # Query parameters
    page = request.query_params.get("page", "1")
    
    # Path parameters
    user_id = request.path_params.get("user_id")
    
    # JSON body
    data = await request.json()
    
    # Form data
    form_data = await request.form()
    
    # Files
    files = await request.form()
    
    # Client information
    client_ip = request.client.host
    
    return ORJSONResponse({"received": "data"})
```

### Response Types

```python
from zestapi import ORJSONResponse
from starlette.responses import JSONResponse, HTMLResponse

# High-performance JSON response (recommended)
return ORJSONResponse({
    "message": "Success",
    "data": {"key": "value"}
}, status_code=200)

# Standard JSON response
return JSONResponse({
    "message": "Success"
}, status_code=200)

# HTML response
return HTMLResponse("<h1>Hello World</h1>")
```

### Status Codes

```python
# Success responses
return ORJSONResponse({"data": "success"}, status_code=200)  # OK
return ORJSONResponse({"created": "item"}, status_code=201)  # Created
return ORJSONResponse({}, status_code=204)  # No Content

# Error responses
return ORJSONResponse({"error": "Not found"}, status_code=404)  # Not Found
return ORJSONResponse({"error": "Bad request"}, status_code=400)  # Bad Request
return ORJSONResponse({"error": "Unauthorized"}, status_code=401)  # Unauthorized
return ORJSONResponse({"error": "Forbidden"}, status_code=403)  # Forbidden
return ORJSONResponse({"error": "Server error"}, status_code=500)  # Internal Server Error
```

## Authentication & Security

### JWT Authentication

ZestAPI includes built-in JWT authentication:

```python
from zestapi import ZestAPI, Settings, create_access_token
from datetime import timedelta

# Configure JWT settings
settings = Settings()
settings.jwt_secret = "your-super-secret-key"
settings.jwt_access_token_expire_minutes = 30

app_instance = ZestAPI(settings=settings)

# Create JWT token
@route("/login", methods=["POST"])
async def login(request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    
    # Validate credentials (implement your logic)
    if username == "admin" and password == "password":
        token = create_access_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=30)
        )
        return ORJSONResponse({"access_token": token})
    
    return ORJSONResponse(
        {"error": "Invalid credentials"}, 
        status_code=401
    )
```

### Protected Routes

```python
from zestapi import requires_auth

@route("/protected", methods=["GET"])
@requires_auth
async def protected_route(request):
    # This route requires authentication
    return ORJSONResponse({"message": "Protected data"})
```

### Security Best Practices

1. **Use Environment Variables**: Never hardcode secrets
2. **Strong JWT Secrets**: Use cryptographically strong secrets
3. **HTTPS in Production**: Always use HTTPS in production
4. **Input Validation**: Validate all user inputs
5. **Rate Limiting**: Enable rate limiting for public endpoints

```python
# .env file
JWT_SECRET=your-super-secret-key-change-in-production
DEBUG=false
RATE_LIMIT=100/minute
```

## Middleware

### Built-in Middleware

ZestAPI includes several built-in middleware:

1. **ErrorHandlingMiddleware**: Comprehensive error handling
2. **RequestLoggingMiddleware**: Request/response logging
3. **RateLimitMiddleware**: Rate limiting
4. **CORSMiddleware**: Cross-origin resource sharing
5. **AuthenticationMiddleware**: JWT authentication

### Custom Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Pre-processing
        print(f"Processing {request.method} {request.url}")
        
        # Call next middleware/route
        response = await call_next(request)
        
        # Post-processing
        response.headers["X-Custom-Header"] = "Custom Value"
        
        return response

# Add middleware to your app
app_instance.add_middleware(CustomMiddleware)
```

## Error Handling

### Built-in Error Handling

ZestAPI provides comprehensive error handling out of the box:

```python
# These exceptions are automatically handled
raise ValueError("Validation error")  # Returns 400
raise PermissionError("Access denied")  # Returns 403
raise FileNotFoundError("Resource not found")  # Returns 404
```

### Custom Exception Handlers

```python
from starlette.exceptions import HTTPException

async def custom_exception_handler(request, exc):
    return ORJSONResponse({
        "error": str(exc),
        "custom_field": "custom_value"
    }, status_code=500)

# Register custom exception handler
app_instance.add_exception_handler(Exception, custom_exception_handler)
```

### Error Response Format

```json
{
  "error": {
    "code": 400,
    "message": "Validation error",
    "type": "ValidationError",
    "request_id": "abc123",
    "timestamp": 1640995200.0,
    "hint": "Check your request parameters and data format"
  }
}
```

## Rate Limiting

### Configuration

```python
from zestapi import Settings

settings = Settings()
settings.rate_limit = "100/minute"  # 100 requests per minute
# Other options: "10/second", "1000/hour", "10000/day"

app_instance = ZestAPI(settings=settings)
```

### Rate Limit Headers

Responses include rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Window: 60
```

### Rate Limit Response

When rate limit is exceeded:

```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded",
    "type": "RateLimitExceeded"
  }
}
```

## WebSocket Support

### Basic WebSocket

```python
from zestapi import websocket_route
import json

@websocket_route("/ws")
async def websocket_handler(websocket):
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_text()
            data = json.loads(message)
            
            # Process message
            response = {"echo": data}
            
            # Send response
            await websocket.send_text(json.dumps(response))
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
```

### WebSocket with Rooms

```python
from zestapi import websocket_route
import json

# Store active connections
connections = {}

@websocket_route("/ws/{room}")
async def chat_room(websocket):
    room = websocket.path_params["room"]
    
    # Add to room
    if room not in connections:
        connections[room] = []
    connections[room].append(websocket)
    
    await websocket.accept()
    
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            # Broadcast to room
            for conn in connections[room]:
                if conn != websocket:
                    await conn.send_text(message)
                    
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Remove from room
        if room in connections:
            connections[room].remove(websocket)
        await websocket.close()
```

## Plugin System

### Creating Plugins

```python
# app/plugins/my_plugin.py
from starlette.responses import JSONResponse

class MyPlugin:
    def __init__(self, app):
        self.app = app
    
    def register(self):
        # Add routes
        @self.app.route("/plugin/status", methods=["GET"])
        async def plugin_status(request):
            return JSONResponse({
                "plugin": "my_plugin",
                "status": "active"
            })
        
        # Add middleware
        # Add custom functionality
        print("MyPlugin registered successfully")

# Function-based plugin
def register_plugin(app):
    @app.route("/plugin/function", methods=["GET"])
    async def plugin_function(request):
        return JSONResponse({"function": "plugin"})
```

### Enabling Plugins

```python
# In your .env file
ENABLED_PLUGINS=my_plugin,another_plugin

# Or in your settings
settings = Settings()
settings.enabled_plugins = ["my_plugin", "another_plugin"]
```

## Configuration

### Environment Variables

ZestAPI uses environment variables for configuration:

```bash
# .env file
JWT_SECRET=your-super-secret-key
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
RATE_LIMIT=100/minute
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
```

### Settings Class

```python
from zestapi import Settings

settings = Settings()

# JWT Configuration
settings.jwt_secret = "your-secret-key"
settings.jwt_algorithm = "HS256"
settings.jwt_access_token_expire_minutes = 30

# Server Configuration
settings.host = "0.0.0.0"
settings.port = 8000
settings.debug = True
settings.reload = False

# Rate Limiting
settings.rate_limit = "100/minute"

# CORS Configuration
settings.cors_origins = ["*"]
settings.cors_allow_credentials = True
settings.cors_allow_methods = ["*"]
settings.cors_allow_headers = ["*"]

# Logging
settings.log_level = "INFO"

# Plugins
settings.enabled_plugins = ["my_plugin"]
```

## Deployment

### Development

```bash
python main.py
```

### Production with Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration

```python
# main.py
import os
from zestapi import ZestAPI, Settings

# Load environment variables
settings = Settings()

# Production settings
if os.getenv("ENVIRONMENT") == "production":
    settings.debug = False
    settings.log_level = "WARNING"
    settings.rate_limit = "1000/hour"

app_instance = ZestAPI(settings=settings)
app = app_instance.app
```

## Best Practices

### 1. Project Structure

```
my-api/
├── main.py
├── .env
├── requirements.txt
├── app/
│   ├── routes/
│   ├── plugins/
│   ├── models/
│   └── utils/
└── tests/
```

### 2. Error Handling

```python
@route("/users/{user_id}")
async def get_user(request):
    try:
        user_id = int(request.path_params["user_id"])
        # ... logic
    except ValueError:
        return ORJSONResponse(
            {"error": "Invalid user ID"}, 
            status_code=400
        )
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return ORJSONResponse(
            {"error": "Internal server error"}, 
            status_code=500
        )
```

### 3. Input Validation

```python
from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v

@route("/users", methods=["POST"])
async def create_user(request):
    try:
        data = await request.json()
        user_data = UserCreate(**data)
        # ... create user
    except ValueError as e:
        return ORJSONResponse(
            {"error": "Validation error", "details": str(e)},
            status_code=400
        )
```

### 4. Logging

```python
import logging

logger = logging.getLogger(__name__)

@route("/users")
async def get_users(request):
    logger.info(f"Getting users from {request.client.host}")
    # ... logic
    logger.info(f"Returned {len(users)} users")
    return ORJSONResponse({"users": users})
```

### 5. Security

```python
# Use environment variables for secrets
import os
from zestapi import Settings

settings = Settings()
settings.jwt_secret = os.getenv("JWT_SECRET")

# Validate inputs
@route("/search")
async def search(request):
    query = request.query_params.get("q", "")
    if len(query) > 100:
        return ORJSONResponse(
            {"error": "Query too long"}, 
            status_code=400
        )
```

## Examples

### Basic CRUD API

```python
# app/routes/users.py
from zestapi import route, ORJSONResponse
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

users_db = {}
user_id_counter = 1

@route("/users", methods=["GET"])
async def get_users(request):
    return ORJSONResponse({"users": list(users_db.values())})

@route("/users/{user_id}", methods=["GET"])
async def get_user(request):
    user_id = int(request.path_params["user_id"])
    if user_id not in users_db:
        return ORJSONResponse({"error": "User not found"}, status_code=404)
    return ORJSONResponse({"user": users_db[user_id]})

@route("/users", methods=["POST"])
async def create_user(request):
    global user_id_counter
    data = await request.json()
    user_data = UserCreate(**data)
    
    new_user = {"id": user_id_counter, **user_data.model_dump()}
    users_db[user_id_counter] = new_user
    user_id_counter += 1
    
    return ORJSONResponse({"user": new_user}, status_code=201)
```

### Authentication API

```python
# app/routes/auth.py
from zestapi import route, ORJSONResponse, create_access_token
from datetime import timedelta

@route("/auth/login", methods=["POST"])
async def login(request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    
    # Validate credentials (implement your logic)
    if username == "admin" and password == "password":
        token = create_access_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=30)
        )
        return ORJSONResponse({"access_token": token})
    
    return ORJSONResponse(
        {"error": "Invalid credentials"}, 
        status_code=401
    )

@route("/auth/profile", methods=["GET"])
async def get_profile(request):
    # This would be protected in real app
    return ORJSONResponse({"username": "admin"})
```

### WebSocket Chat

```python
# app/routes/chat.py
from zestapi import websocket_route
import json

connections = {}

@websocket_route("/ws/chat")
async def chat_handler(websocket):
    await websocket.accept()
    
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            # Broadcast to all connections
            for conn in connections.values():
                await conn.send_text(message)
                
    except Exception as e:
        print(f"Chat error: {e}")
    finally:
        await websocket.close()
```

## CLI Tools

ZestAPI includes a CLI tool for project management:

```bash
# Initialize a new project
zest init

# Generate a new route
zest generate route users

# Generate a new plugin
zest generate plugin my_plugin

# View route map
zest route-map

# Show version
zest version
```

## Testing

### Basic Test Example

```python
# tests/test_api.py
import pytest
from starlette.testclient import TestClient
from main import app_instance

@pytest.fixture
def client():
    app = app_instance.app
    return TestClient(app)

def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_create_user(client):
    user_data = {"name": "Test User", "email": "test@example.com"}
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Port Already in Use**: Change port in settings or kill existing process
3. **JWT Errors**: Check JWT secret configuration
4. **Route Not Found**: Verify route decorators and file structure
5. **CORS Issues**: Configure CORS settings properly

### Debug Mode

Enable debug mode for detailed error messages:

```python
settings = Settings()
settings.debug = True
app_instance = ZestAPI(settings=settings)
```

### Logging

Configure logging for better debugging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Support

- **Documentation**: [GitHub Repository](https://github.com/madnansultandotme/zestapi-python)
- **Issues**: [GitHub Issues](https://github.com/madnansultandotme/zestapi-python/issues)
- **Email**: info.adnansultan@gmail.com

---

This user guide covers the essential aspects of building applications with ZestAPI. For more advanced features and examples, refer to the examples directory in the repository. 