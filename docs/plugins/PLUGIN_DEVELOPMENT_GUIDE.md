# ZestAPI Plugin Development Guide

This comprehensive guide covers how to create, configure, and deploy plugins for ZestAPI. Plugins allow you to extend the framework with custom functionality, middleware, and integrations.

## Table of Contents

1. [Plugin Architecture](#plugin-architecture)
2. [Plugin Types](#plugin-types)
3. [Creating Your First Plugin](#creating-your-first-plugin)
4. [Plugin Structure](#plugin-structure)
5. [Plugin Lifecycle](#plugin-lifecycle)
6. [Middleware Plugins](#middleware-plugins)
7. [Route Extension Plugins](#route-extension-plugins)
8. [Service Integration Plugins](#service-integration-plugins)
9. [Configuration and Settings](#configuration-and-settings)
10. [Testing Plugins](#testing-plugins)
11. [Publishing Plugins](#publishing-plugins)
12. [Best Practices](#best-practices)
13. [Example Plugins](#example-plugins)

## Plugin Architecture

ZestAPI uses a modular plugin architecture that allows developers to:

- **Extend Core Functionality**: Add new features to the framework
- **Custom Middleware**: Create request/response processing middleware
- **Third-party Integrations**: Connect with external services and APIs
- **Custom Validators**: Add specialized data validation
- **Authentication Providers**: Implement custom auth mechanisms
- **Database Connectors**: Add support for different databases

### Plugin Discovery

ZestAPI automatically discovers plugins in:
1. The `app/plugins/` directory
2. Installed Python packages with the `zestapi_plugin` entry point
3. Plugins registered via configuration

## Plugin Types

### 1. Middleware Plugins
Process requests and responses at various stages of the request lifecycle.

### 2. Route Extension Plugins
Add new routes, endpoints, or modify existing routing behavior.

### 3. Service Integration Plugins
Connect with external services like databases, caches, message queues, etc.

### 4. Validation Plugins
Provide custom validation logic for request data.

### 5. Authentication Plugins
Implement custom authentication and authorization mechanisms.

### 6. Utility Plugins
Provide helper functions and utilities for other parts of the application.

## Creating Your First Plugin

Let's create a simple rate limiting plugin:

### Step 1: Create Plugin Directory

```bash
mkdir app/plugins/rate_limiter
cd app/plugins/rate_limiter
```

### Step 2: Create Plugin Files

Create the following files:

#### `__init__.py`
```python
"""
Rate Limiter Plugin for ZestAPI
Provides configurable rate limiting functionality
"""

from .plugin import RateLimiterPlugin

__version__ = "1.0.0"
__plugin_name__ = "rate_limiter"
__plugin_class__ = RateLimiterPlugin

# Export the plugin class
__all__ = ["RateLimiterPlugin"]
```

#### `plugin.py`
```python
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from zestapi.core.plugin import BasePlugin
from zestapi.core.middleware import BaseMiddleware

class RateLimiterMiddleware(BaseMiddleware):
    def __init__(self, requests_per_minute: int = 60, window_size: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size
        self.client_requests: Dict[str, list] = {}
    
    async def process_request(self, request):
        client_ip = self.get_client_ip(request)
        current_time = datetime.utcnow()
        
        # Clean old requests
        self.cleanup_old_requests(client_ip, current_time)
        
        # Check rate limit
        if self.is_rate_limited(client_ip, current_time):
            from zestapi import ORJSONResponse
            return ORJSONResponse(
                {"error": "Rate limit exceeded"}, 
                status_code=429
            )
        
        # Record this request
        self.record_request(client_ip, current_time)
        return None  # Continue processing
    
    def get_client_ip(self, request) -> str:
        # Try to get real IP from headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client address
        return request.client.host if request.client else "unknown"
    
    def cleanup_old_requests(self, client_ip: str, current_time: datetime):
        if client_ip in self.client_requests:
            cutoff_time = current_time - timedelta(seconds=self.window_size)
            self.client_requests[client_ip] = [
                req_time for req_time in self.client_requests[client_ip]
                if req_time > cutoff_time
            ]
    
    def is_rate_limited(self, client_ip: str, current_time: datetime) -> bool:
        if client_ip not in self.client_requests:
            return False
        
        return len(self.client_requests[client_ip]) >= self.requests_per_minute
    
    def record_request(self, client_ip: str, current_time: datetime):
        if client_ip not in self.client_requests:
            self.client_requests[client_ip] = []
        self.client_requests[client_ip].append(current_time)

class RateLimiterPlugin(BasePlugin):
    name = "rate_limiter"
    version = "1.0.0"
    description = "Configurable rate limiting for API endpoints"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.requests_per_minute = self.config.get("requests_per_minute", 60)
        self.window_size = self.config.get("window_size", 60)
        self.middleware = None
    
    async def initialize(self, app):
        """Initialize the plugin with the ZestAPI app instance"""
        self.middleware = RateLimiterMiddleware(
            requests_per_minute=self.requests_per_minute,
            window_size=self.window_size
        )
        
        # Register middleware with the app
        app.add_middleware(self.middleware)
        
        self.logger.info(f"Rate limiter initialized: {self.requests_per_minute} requests per minute")
    
    async def cleanup(self):
        """Cleanup when plugin is unloaded"""
        if self.middleware:
            self.middleware.client_requests.clear()
        self.logger.info("Rate limiter cleanup completed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status information"""
        client_count = len(self.middleware.client_requests) if self.middleware else 0
        return {
            "active": self.is_active,
            "requests_per_minute": self.requests_per_minute,
            "window_size": self.window_size,
            "tracked_clients": client_count
        }
```

#### `config.py`
```python
from typing import Dict, Any
from pydantic import BaseModel, field_validator

class RateLimiterConfig(BaseModel):
    """Configuration for Rate Limiter Plugin"""
    
    requests_per_minute: int = 60
    window_size: int = 60  # seconds
    enabled: bool = True
    excluded_paths: list = []
    
    @field_validator('requests_per_minute')
    @classmethod
    def validate_requests_per_minute(cls, v):
        if v <= 0:
            raise ValueError('requests_per_minute must be positive')
        return v
    
    @field_validator('window_size')
    @classmethod
    def validate_window_size(cls, v):
        if v <= 0:
            raise ValueError('window_size must be positive')
        return v

# Default configuration
DEFAULT_CONFIG = {
    "requests_per_minute": 60,
    "window_size": 60,
    "enabled": True,
    "excluded_paths": ["/health", "/metrics"]
}
```

### Step 3: Create Plugin Manifest

#### `plugin.yaml`
```yaml
name: rate_limiter
version: 1.0.0
description: Configurable rate limiting for API endpoints
author: Your Name
email: info.adnansultan@gmail.com
license: MIT
homepage: https://github.com/madnansultandotme/zestapi-rate-limiter

# Plugin metadata
type: middleware
category: security
tags:
  - rate-limiting
  - security
  - middleware

# Dependencies
dependencies:
  zestapi: ">=1.0.0"
  
# Configuration schema
config_schema: config.RateLimiterConfig

# Entry points
entry_points:
  middleware:
    - RateLimiterMiddleware
  
# Supported ZestAPI versions
zestapi_version: ">=1.0.0"

# Plugin capabilities
capabilities:
  - middleware
  - configurable
  - async
```

### Step 4: Register the Plugin

#### In your main application (`main.py`):
```python
from zestapi import ZestAPI
from app.plugins.rate_limiter import RateLimiterPlugin

app_instance = ZestAPI()

# Register the plugin
rate_limiter_config = {
    "requests_per_minute": 100,
    "window_size": 60
}

app_instance.register_plugin(RateLimiterPlugin(rate_limiter_config))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_instance, host="0.0.0.0", port=8000)
```

## Plugin Structure

### Required Files

Every plugin should have the following structure:

```
app/plugins/your_plugin/
├── __init__.py          # Plugin exports and metadata
├── plugin.py            # Main plugin class
├── config.py           # Configuration models
├── plugin.yaml         # Plugin manifest
├── README.md           # Documentation
├── requirements.txt    # Dependencies
└── tests/              # Plugin tests
    ├── __init__.py
    ├── test_plugin.py
    └── conftest.py
```

### Optional Files

```
app/plugins/your_plugin/
├── middleware.py       # Custom middleware
├── routes.py          # Additional routes
├── services.py        # Service integrations
├── validators.py      # Custom validators
├── exceptions.py      # Custom exceptions
├── utils.py           # Utility functions
└── assets/            # Static assets
    ├── templates/
    └── static/
```

## Plugin Lifecycle

Plugins go through several lifecycle stages:

### 1. Discovery
ZestAPI discovers plugins during application startup.

### 2. Loading
Plugin classes are imported and instantiated.

### 3. Initialization
The `initialize()` method is called with the app instance.

### 4. Registration
Plugin components (middleware, routes, etc.) are registered.

### 5. Runtime
Plugin operates during request processing.

### 6. Cleanup
The `cleanup()` method is called during shutdown.

### Lifecycle Hooks

```python
class MyPlugin(BasePlugin):
    async def initialize(self, app):
        """Called when plugin is loaded"""
        pass
    
    async def on_startup(self, app):
        """Called when application starts"""
        pass
    
    async def on_shutdown(self, app):
        """Called when application shuts down"""
        pass
    
    async def cleanup(self):
        """Called when plugin is unloaded"""
        pass
```

## Middleware Plugins

Middleware plugins process requests and responses:

```python
from zestapi.core.middleware import BaseMiddleware

class AuthMiddleware(BaseMiddleware):
    async def process_request(self, request):
        """Process incoming request"""
        # Return response to short-circuit, or None to continue
        token = request.headers.get("Authorization")
        if not token:
            return ORJSONResponse({"error": "Auth required"}, status_code=401)
        return None
    
    async def process_response(self, request, response):
        """Process outgoing response"""
        response.headers["X-Custom-Header"] = "Plugin-Added"
        return response
    
    async def process_exception(self, request, exception):
        """Handle exceptions"""
        self.logger.error(f"Request failed: {exception}")
        return None  # Let default handler process
```

## Route Extension Plugins

Add new routes to your application:

```python
from zestapi import route, ORJSONResponse

class APIDocsPlugin(BasePlugin):
    async def initialize(self, app):
        # Add routes
        app.add_route("/docs", self.serve_docs)
        app.add_route("/docs/openapi.json", self.openapi_spec)
    
    async def serve_docs(self, request):
        """Serve API documentation"""
        return HTMLResponse(self.generate_docs_html())
    
    async def openapi_spec(self, request):
        """Serve OpenAPI specification"""
        return ORJSONResponse(self.generate_openapi_spec())
```

## Service Integration Plugins

Connect with external services:

```python
import redis
from typing import Optional

class RedisPlugin(BasePlugin):
    def __init__(self, config):
        super().__init__(config)
        self.redis_client: Optional[redis.Redis] = None
    
    async def initialize(self, app):
        # Connect to Redis
        self.redis_client = redis.Redis(
            host=self.config.get("host", "localhost"),
            port=self.config.get("port", 6379),
            db=self.config.get("db", 0)
        )
        
        # Make client available to app
        app.state.redis = self.redis_client
        
        # Test connection
        await self.redis_client.ping()
        self.logger.info("Connected to Redis")
    
    async def cleanup(self):
        if self.redis_client:
            await self.redis_client.close()
```

## Configuration and Settings

### Environment-based Configuration

```python
import os
from typing import Dict, Any

class PluginConfig:
    @classmethod
    def from_env(cls, prefix: str = "PLUGIN_") -> Dict[str, Any]:
        config = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                config[config_key] = value
        return config

# Usage
config = PluginConfig.from_env("RATE_LIMITER_")
plugin = RateLimiterPlugin(config)
```

### File-based Configuration

```python
import yaml
import json
from pathlib import Path

class ConfigLoader:
    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            return json.load(f)

# Usage
config = ConfigLoader.load_yaml("config/rate_limiter.yaml")
plugin = RateLimiterPlugin(config)
```

## Testing Plugins

### Unit Tests

```python
import pytest
from unittest.mock import Mock, AsyncMock
from your_plugin import YourPlugin

class TestYourPlugin:
    @pytest.fixture
    def plugin_config(self):
        return {
            "enabled": True,
            "setting1": "value1"
        }
    
    @pytest.fixture
    def plugin(self, plugin_config):
        return YourPlugin(plugin_config)
    
    @pytest.mark.asyncio
    async def test_plugin_initialization(self, plugin):
        app_mock = Mock()
        await plugin.initialize(app_mock)
        assert plugin.is_active
    
    @pytest.mark.asyncio
    async def test_plugin_functionality(self, plugin):
        # Test your plugin's functionality
        result = await plugin.some_method()
        assert result == expected_value
```

### Integration Tests

```python
import pytest
from httpx import AsyncClient
from zestapi import ZestAPI
from your_plugin import YourPlugin

@pytest.mark.asyncio
async def test_plugin_integration():
    app = ZestAPI()
    plugin = YourPlugin({"enabled": True})
    app.register_plugin(plugin)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
```

## Publishing Plugins

### Package Structure for Distribution

```
zestapi-your-plugin/
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── src/
│   └── zestapi_your_plugin/
│       ├── __init__.py
│       ├── plugin.py
│       ├── config.py
│       └── middleware.py
├── tests/
└── docs/
```

### setup.py

```python
from setuptools import setup, find_packages

setup(
    name="zestapi-your-plugin",
    version="1.0.0",
    description="Your plugin description",
    author="Muhammad Adnan Sultan",
    author_email="info.adnansultan@gmail.com",
    url="https://github.com/madnansultandotme/zestapi-your-plugin",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "zestapi>=1.0.0",
    ],
    entry_points={
        "zestapi.plugins": [
            "your_plugin = zestapi_your_plugin:YourPlugin",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8+",
        "Framework :: ZestAPI",
    ],
    python_requires=">=3.8",
)
```

### PyPI Distribution

```bash
# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI
pip install twine
twine upload dist/*
```

## Best Practices

### 1. Plugin Design

- **Single Responsibility**: Each plugin should have a clear, single purpose
- **Configurable**: Make your plugin configurable via environment variables or config files
- **Async-First**: Use async/await for all I/O operations
- **Error Handling**: Implement proper error handling and logging

### 2. Performance

- **Lazy Loading**: Load resources only when needed
- **Connection Pooling**: Use connection pools for external services
- **Caching**: Cache expensive operations when appropriate
- **Resource Cleanup**: Always clean up resources in the cleanup method

### 3. Security

- **Input Validation**: Validate all configuration and input data
- **Secure Defaults**: Use secure default configurations
- **Sensitive Data**: Don't log sensitive information
- **Permissions**: Request minimal necessary permissions

### 4. Compatibility

- **Version Pinning**: Specify compatible ZestAPI versions
- **Backwards Compatibility**: Maintain backwards compatibility when possible
- **Deprecation Warnings**: Warn users about deprecated features

### 5. Documentation

- **README**: Include comprehensive setup and usage instructions
- **API Docs**: Document all public methods and configuration options
- **Examples**: Provide working examples
- **Changelog**: Maintain a changelog for version history

## Example Plugins

### 1. Database Connection Plugin

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class DatabasePlugin(BasePlugin):
    async def initialize(self, app):
        database_url = self.config.get("database_url")
        self.engine = create_async_engine(database_url)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        app.state.db = self.session_factory
```

### 2. CORS Plugin

```python
class CORSPlugin(BasePlugin):
    async def initialize(self, app):
        middleware = CORSMiddleware(
            allow_origins=self.config.get("allow_origins", ["*"]),
            allow_credentials=self.config.get("allow_credentials", True),
            allow_methods=self.config.get("allow_methods", ["*"]),
            allow_headers=self.config.get("allow_headers", ["*"]),
        )
        app.add_middleware(middleware)
```

### 3. Metrics Plugin

```python
from prometheus_client import Counter, Histogram

class MetricsPlugin(BasePlugin):
    def __init__(self, config):
        super().__init__(config)
        self.request_count = Counter('http_requests_total', 'Total HTTP requests')
        self.request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
    
    async def initialize(self, app):
        app.add_middleware(MetricsMiddleware(self))
        app.add_route("/metrics", self.metrics_endpoint)
```

This comprehensive guide provides everything you need to create powerful, production-ready plugins for ZestAPI. Start with simple plugins and gradually add more sophisticated features as you become familiar with the plugin system.
