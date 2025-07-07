# ZestAPI Documentation

ZestAPI is a modern, high-performance Python web framework designed to combine the best features of Flask and FastAPI while addressing their common pain points.

## Features

### 🚀 **High Performance**
- Built on Starlette (ASGI 3.0)
- orjson for ultra-fast JSON serialization
- Async/await support throughout
- Production-ready performance optimizations

### 🛠 **Developer Experience**
- Auto-discovery of routes from directory structure
- CLI tools for rapid development
- Built-in validation with Pydantic
- Comprehensive error handling
- Hot reload support

### 🔒 **Security First**
- JWT authentication built-in
- Rate limiting middleware
- CORS support out of the box
- Secure defaults

### 🧩 **Extensible**
- Plugin system for modular functionality
- Middleware support
- Easy integration with existing Python libraries

### 📊 **Production Ready**
- Request/response logging
- Health checks
- Performance monitoring
- Environment-based configuration

## Quick Start

### Installation

```bash
pip install zestapi
```

### Create a New Project

```bash
zest init
cd my-zestapi-project
python main.py
```

### Basic Application

```python
from zestapi import ZestAPI, ORJSONResponse

app_instance = ZestAPI()

async def homepage(request):
    return ORJSONResponse({"message": "Hello, ZestAPI!"})

app_instance.add_route("/", homepage)
app = app_instance.create_app()

if __name__ == "__main__":
    app_instance.run()
```

## CLI Commands

### Initialize Project
```bash
zest init
```

### Generate Routes
```bash
zest generate route users
zest generate route products
```

### Generate Plugins
```bash
zest generate plugin analytics
```

### View Route Map
```bash
zest route-map
```

## Route Definition

### Manual Route Registration
```python
async def get_users(request):
    return ORJSONResponse({"users": []})

app_instance.add_route("/users", get_users, methods=["GET"])
```

### File-based Route Discovery
Create files in `app/routes/` directory:

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
    return ORJSONResponse({"created": True, "data": data}, status_code=201)
```

## Configuration

### Environment Variables (.env)
```bash
JWT_SECRET=your-super-secret-key
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
RATE_LIMIT=100/minute
CORS_ORIGINS=["*"]
```

### Programmatic Configuration
```python
from zestapi.core.settings import Settings

settings = Settings()
settings.jwt_secret = "custom-secret"
settings.rate_limit = "50/minute"

app_instance = ZestAPI(settings=settings)
```

## Authentication

### JWT Token Creation
```python
from zestapi import create_access_token
from datetime import timedelta

token = create_access_token(
    data={"sub": "user123", "role": "admin"},
    expires_delta=timedelta(hours=1)
)
```

### Using JWT Tokens
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/protected
```

## Middleware

ZestAPI includes several built-in middleware:

- **Rate Limiting**: Configurable per-endpoint rate limiting
- **CORS**: Cross-origin resource sharing support
- **Authentication**: JWT-based authentication
- **Error Handling**: Comprehensive error handling and logging
- **Request Logging**: Automatic request/response logging

## WebSocket Support

```python
async def websocket_endpoint(websocket):
    await websocket.accept()
    await websocket.send_text("Hello WebSocket!")
    await websocket.close()

app_instance.add_websocket_route("/ws", websocket_endpoint)
```

## Plugin System

### Creating a Plugin
```python
# app/plugins/my_plugin.py
class MyPlugin:
    def __init__(self, app):
        self.app = app

    def register(self):
        @self.app.route("/plugin-endpoint")
        async def plugin_endpoint(request):
            return {"plugin": "active"}
```

### Enabling Plugins
Add to your `.env` file:
```bash
ENABLED_PLUGINS=["my_plugin", "analytics"]
```

## Error Handling

ZestAPI provides comprehensive error handling:

```python
async def error_prone_endpoint(request):
    raise ValueError("Something went wrong")
    
# Returns:
# {
#   "error": {
#     "code": 500,
#     "message": "Internal server error",
#     "type": "InternalError"
#   }
# }
```

## Validation

Using Pydantic for request validation:

```python
from pydantic import BaseModel, field_validator

class UserModel(BaseModel):
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
    user = UserModel(**data)  # Automatic validation
    return ORJSONResponse({"user": user.model_dump()})
```

## Performance Features

- **orjson**: 2-3x faster JSON serialization than standard library
- **Rate Limiting**: Built-in protection against abuse
- **Response Caching**: Via middleware
- **Process Time Headers**: Automatic performance monitoring

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

### Environment Configuration
```bash
# Production .env
JWT_SECRET=your-production-secret-key
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=WARNING
RATE_LIMIT=1000/minute
```

## Comparison with Flask and FastAPI

| Feature | ZestAPI | FastAPI | Flask |
|---------|---------|---------|-------|
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Auto-routing | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| Built-in Auth | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Rate Limiting | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| CLI Tools | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Plugin System | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Learning Curve | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Best Practices

1. **Use Environment Variables**: Configure your application through environment variables
2. **Structure Routes**: Organize routes in separate files under `app/routes/`
3. **Error Handling**: Let ZestAPI handle errors automatically, but provide meaningful error messages
4. **Authentication**: Use JWT tokens for stateless authentication
5. **Rate Limiting**: Configure appropriate rate limits for your API
6. **Logging**: Use the built-in logging middleware for monitoring
7. **Testing**: Write comprehensive tests using the TestClient

## Examples

See the `demo/` directory for a complete example application showcasing all ZestAPI features.

## Contributing

We welcome contributions! Please see our contributing guidelines for more information.

## License

ZestAPI is licensed under the MIT License.
