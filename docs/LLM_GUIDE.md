# ZestAPI - LLM Developer Guide

## Quick Reference for AI Assistants

ZestAPI is a modern Python web framework optimized for rapid API development with built-in production features.

### Core Concept
```python
from zestapi import ZestAPI
app = ZestAPI()  # Auto-discovers routes from app/routes/
```

## Essential Patterns

### 1. Basic Application Setup
```python
# main.py
from zestapi import ZestAPI

app_instance = ZestAPI()

# Manual route (immediate use)
@app_instance.route("/health")
async def health_check(request):
    return {"status": "ok"}

# Get ASGI app for deployment
app = app_instance.app

if __name__ == "__main__":
    app_instance.run()  # Development server
```

### 2. File-Based Routes (Recommended)
```python
# app/routes/users.py
from zestapi import route, ORJSONResponse

@route("/users", methods=["GET"])
async def list_users(request):
    return ORJSONResponse({"users": []})

@route("/users/{user_id}", methods=["GET"])
async def get_user(request):
    user_id = request.path_params["user_id"]
    return ORJSONResponse({"user_id": user_id})

@route("/users", methods=["POST"])
async def create_user(request):
    data = await request.json()
    return ORJSONResponse({"created": True}, status_code=201)
```

### 3. Request Handling Patterns
```python
# Path parameters
async def get_item(request):
    item_id = request.path_params["item_id"]
    
# Query parameters
async def search_items(request):
    query = request.query_params.get("q", "")
    limit = int(request.query_params.get("limit", "10"))
    
# JSON body
async def create_item(request):
    data = await request.json()
    
# Form data
async def upload_file(request):
    form = await request.form()
    file = form["file"]
    
# Headers
async def protected_route(request):
    auth_header = request.headers.get("authorization")
```

### 4. Response Patterns
```python
from zestapi import ORJSONResponse

# JSON response (fast orjson)
return ORJSONResponse({"data": "value"})

# Custom status
return ORJSONResponse({"created": True}, status_code=201)

# Headers
return ORJSONResponse(
    {"data": "value"}, 
    headers={"X-Custom": "value"}
)

# Error responses (handled automatically)
raise ValueError("Bad input")  # → 400
raise PermissionError("Access denied")  # → 403
raise FileNotFoundError("Not found")  # → 404
```

### 5. Authentication
```python
# Create JWT token
from zestapi import create_access_token
token = create_access_token({"sub": "user123"})

# Protected route
async def protected(request):
    user = request.user  # Available when authenticated
    return {"user": user.display_name}

# Check authentication
if request.user.is_authenticated:
    # User is logged in
```

### 6. Environment Configuration
```bash
# .env file
JWT_SECRET=your-production-secret-key
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
RATE_LIMIT=100/minute
CORS_ORIGINS=["https://yourdomain.com"]
```

### 7. Plugin System
```python
# app/plugins/analytics.py
def register(app):
    @app.route("/analytics")
    async def analytics_endpoint(request):
        return {"analytics": "data"}

# Enable in .env
ENABLED_PLUGINS=["analytics"]
```

### 8. WebSocket Support
```python
async def websocket_endpoint(websocket):
    await websocket.accept()
    data = await websocket.receive_text()
    await websocket.send_text(f"Echo: {data}")
    await websocket.close()

app_instance.add_websocket_route("/ws", websocket_endpoint)
```

### 9. Validation with Pydantic
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

async def create_user(request):
    data = await request.json()
    user = UserCreate(**data)  # Auto-validation
    return ORJSONResponse(user.model_dump())
```

### 10. Error Handling
```python
# Custom error handler
async def validation_error_handler(request, exc):
    return ORJSONResponse(
        {"error": "Validation failed", "details": str(exc)},
        status_code=400
    )

app_instance.add_exception_handler(ValueError, validation_error_handler)
```

## CLI Commands
```bash
zest init my-api              # Create new project
zest generate route users     # Generate route file
zest generate plugin auth     # Generate plugin file
zest route-map               # Show all routes
zest version                 # Show version
```

## Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

### Requirements
```txt
zestapi>=1.0.0
uvicorn[standard]>=0.30.0
```

### Production Settings
```python
from zestapi import ZestAPI, Settings

settings = Settings(
    jwt_secret="your-secure-secret",
    debug=False,
    log_level="WARNING",
    rate_limit="1000/minute"
)

app_instance = ZestAPI(settings=settings)
```

## Built-in Features

- **Auto-discovery**: Routes found in `app/routes/` automatically
- **JWT Authentication**: Built-in token creation and validation
- **Rate Limiting**: Configurable per-endpoint protection
- **CORS**: Cross-origin request handling
- **Error Handling**: Comprehensive exception management
- **Request Logging**: Automatic request/response logging
- **Validation**: Pydantic integration for data validation
- **WebSockets**: Real-time communication support
- **Plugin System**: Modular functionality extension

## Common Use Cases

### REST API
```python
# app/routes/api.py
@route("/api/items", methods=["GET"])
async def list_items(request):
    return ORJSONResponse({"items": []})

@route("/api/items", methods=["POST"])
async def create_item(request):
    data = await request.json()
    return ORJSONResponse({"id": 1, **data}, status_code=201)
```

### Microservice
```python
# Lightweight service
from zestapi import ZestAPI

app_instance = ZestAPI()

@app_instance.route("/health")
async def health(request):
    return {"status": "healthy"}

app = app_instance.app  # For deployment
```

### API with Database
```python
# With async database
import asyncpg

async def get_users(request):
    async with asyncpg.create_pool(DATABASE_URL) as pool:
        async with pool.acquire() as conn:
            users = await conn.fetch("SELECT * FROM users")
            return ORJSONResponse([dict(user) for user in users])
```

## Best Practices for LLMs

1. **Always use ORJSONResponse** for JSON (faster than default)
2. **Use file-based routes** for better organization
3. **Handle exceptions properly** (framework provides good defaults)
4. **Set JWT_SECRET** for production
5. **Use environment variables** for configuration
6. **Structure projects** with `app/routes/` and `app/plugins/`
7. **Leverage auto-discovery** instead of manual route registration
8. **Use proper HTTP status codes** in responses

## Framework Architecture

ZestAPI is built on Starlette (ASGI) with these enhancements:
- Auto-discovery system for routes and plugins
- Built-in production middleware (auth, rate limiting, CORS, logging)
- Fast JSON serialization with orjson
- Comprehensive error handling with request tracking
- CLI tools for rapid development
- Environment-based configuration

Perfect for building modern APIs that need to be fast, secure, and maintainable.
