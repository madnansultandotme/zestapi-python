from zestapi import ZestAPI, Settings, ORJSONResponse
import os
import logging

# Production settings
settings = Settings()

# Validate production configuration
if not settings.debug:
    if not settings.jwt_secret or settings.jwt_secret == "your-secret-key":
        raise ValueError("JWT_SECRET must be set for production")
    
    if settings.log_level not in ["WARNING", "ERROR"]:
        logging.warning("Consider using WARNING or ERROR log level in production")

# Create ZestAPI instance with production settings
app_instance = ZestAPI(settings=settings)

# Add custom error handler for production
async def production_error_handler(request, exc):
    """Custom error handler that sanitizes errors in production"""
    if settings.debug:
        # In debug mode, show full error details
        return ORJSONResponse({
            "error": str(exc),
            "type": exc.__class__.__name__,
            "debug": True
        }, status_code=500)
    else:
        # In production, show sanitized error
        return ORJSONResponse({
            "error": "Internal server error",
            "type": "ServerError",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }, status_code=500)

app_instance.add_exception_handler(Exception, production_error_handler)

async def root(request):
    return ORJSONResponse({
        "service": "ZestAPI Production Example",
        "version": "1.0.0",
        "environment": "production" if not settings.debug else "development",
        "status": "operational"
    })

# Add routes
app_instance.add_route("/", root)

# Get ASGI app for deployment
app = app_instance.app

if __name__ == "__main__":
    print("[*] Starting ZestAPI Production Example...")
    print(f"[*] Environment: {'Production' if not settings.debug else 'Development'}")
    print(f"[*] JWT Auth: {'Enabled' if settings.jwt_secret != 'your-secret-key' else 'Disabled'}")
    print(f"[*] Log Level: {settings.log_level}")
    print(f"[*] Rate Limit: {settings.rate_limit}")
    app_instance.run()
