#!/usr/bin/env python3
"""
ZestAPI Plugin System Example
============================

This example demonstrates a plugin system with:
- Request logging plugin
- API key authentication plugin
- Plugin lifecycle management
- Middleware integration

The plugin system allows for modular functionality that can be
enabled/disabled and configured independently.
"""

import asyncio
import logging

from app.plugins.example_plugin.plugin import APIKeyPlugin, RequestLoggerPlugin
from zestapi import ORJSONResponse, ZestAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create ZestAPI instance
app_instance = ZestAPI()

# Plugin storage
app_plugins = []


# Mock middleware processing (simplified for demonstration)
async def plugin_middleware(request, call_next):
    """Process plugins as middleware"""
    response = None

    # Process request middleware
    for plugin in app_plugins:
        if hasattr(plugin, "process_request"):
            response = await plugin.process_request(request)
            if response:
                break

    # If no middleware returned a response, continue with the route
    if not response:
        response = await call_next(request)

    # Process response middleware
    for plugin in app_plugins:
        if hasattr(plugin, "process_response"):
            response = await plugin.process_response(request, response)

    return response


# Note: Middleware processing would be integrated into ZestAPI's middleware system


# Initialize plugins
async def setup_plugins():
    """Setup and initialize plugins"""

    # Request Logger Plugin
    logger_config = {"log_level": "INFO", "include_body": False}
    logger_plugin = RequestLoggerPlugin(logger_config)
    await logger_plugin.initialize(app_instance)

    # API Key Authentication Plugin
    api_key_config = {
        "api_keys": ["test-api-key-123", "admin-key-456", "user-key-789"],
        "header_name": "X-API-Key",
        "protected_paths": ["/protected", "/admin", "/api/secure"],
    }
    api_key_plugin = APIKeyPlugin(api_key_config)
    await api_key_plugin.initialize(app_instance)

    return [logger_plugin, api_key_plugin]


# Store plugins for cleanup
app_plugins.clear()


# Routes
async def root(request):
    return ORJSONResponse(
        {
            "message": "Welcome to ZestAPI Plugin System Example",
            "version": "1.0.0",
            "plugins": (
                [plugin.get_status() for plugin in app_plugins] if app_plugins else []
            ),
            "endpoints": {
                "public": {
                    "root": "GET /",
                    "test": "GET /api/test",
                    "health": "GET /health",
                },
                "protected": {
                    "protected": "GET /protected (requires X-API-Key)",
                    "admin": "GET /admin (requires X-API-Key)",
                    "secure_api": "GET /api/secure (requires X-API-Key)",
                },
            },
            "demo_instructions": {
                "test_logging": "Make requests to any endpoint to see request logging",
                "test_auth": "Use header 'X-API-Key: test-api-key-123' for protected endpoints",
            },
        }
    )


async def api_test(request):
    return ORJSONResponse(
        {
            "message": "This is a test API endpoint",
            "timestamp": "2024-01-01T12:00:00Z",
            "request_method": request.method,
            "request_path": str(request.url.path),
        }
    )


async def protected_endpoint(request):
    # This will be protected by the API key middleware
    api_key = getattr(request.state, "api_key", None)
    return ORJSONResponse(
        {
            "message": "This is a protected endpoint",
            "authenticated": True,
            "api_key_used": api_key or "none",
            "access_granted": True,
        }
    )


async def admin_endpoint(request):
    api_key = getattr(request.state, "api_key", None)
    return ORJSONResponse(
        {
            "message": "Admin endpoint accessed",
            "authenticated": True,
            "api_key_used": api_key or "none",
            "admin_access": True,
            "sensitive_data": "This would contain admin-only information",
        }
    )


async def secure_api_endpoint(request):
    api_key = getattr(request.state, "api_key", None)
    return ORJSONResponse(
        {
            "message": "Secure API endpoint",
            "authenticated": True,
            "api_key_used": api_key or "none",
            "data": {
                "secure_value": 42,
                "protected_info": "This data requires authentication",
            },
        }
    )


async def health_check(request):
    plugin_status = {}
    if app_plugins:
        plugin_status = {plugin.name: plugin.is_active for plugin in app_plugins}

    return ORJSONResponse(
        {
            "status": "healthy",
            "service": "zestapi-plugin-system-example",
            "plugins": plugin_status,
            "middleware_count": len(app_plugins),
        }
    )


async def plugin_status(request):
    """Get detailed plugin status"""
    return ORJSONResponse(
        {
            "plugins": (
                [plugin.get_status() for plugin in app_plugins] if app_plugins else []
            ),
            "total_plugins": len(app_plugins),
            "active_plugins": (
                sum(1 for plugin in app_plugins if plugin.is_active)
                if app_plugins
                else 0
            ),
        }
    )


# Add routes
app_instance.add_route("/", root)
app_instance.add_route("/api/test", api_test)
app_instance.add_route("/protected", protected_endpoint)
app_instance.add_route("/admin", admin_endpoint)
app_instance.add_route("/api/secure", secure_api_endpoint)
app_instance.add_route("/health", health_check)
app_instance.add_route("/api/plugins/status", plugin_status)


# Startup event
async def startup():
    """Initialize plugins on startup"""
    try:
        plugins = await setup_plugins()
        app_plugins.extend(plugins)
        print("[+] Plugin system initialized")
        print("[+] Request logging is active")
        print("[+] API key authentication is active")
        print("\n[*] Test the system:")
        print("  Public endpoints:")
        print("    curl http://localhost:8000/")
        print("    curl http://localhost:8000/api/test")
        print("\n  Protected endpoints (require X-API-Key header):")
        print(
            "    curl -H 'X-API-Key: test-api-key-123' http://localhost:8000/protected"
        )
        print("    curl -H 'X-API-Key: test-api-key-123' http://localhost:8000/admin")
        print(
            "    curl -H 'X-API-Key: test-api-key-123' http://localhost:8000/api/secure"
        )
    except Exception as e:
        print(f"[!] Plugin initialization failed: {e}")


# Shutdown event
async def shutdown():
    """Cleanup plugins on shutdown"""
    try:
        for plugin in app_plugins:
            await plugin.cleanup()
        print("[*] Plugins cleaned up")
    except Exception as e:
        print(f"[!] Plugin cleanup failed: {e}")


# Expose the app for ASGI servers
app = app_instance.app

if __name__ == "__main__":
    # Run startup
    asyncio.run(startup())

    try:
        print("[*] Starting ZestAPI Plugin System Example...")
        print("[*] Server will be available at http://localhost:8000")
        app_instance.run()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    finally:
        # Run cleanup
        asyncio.run(shutdown())
