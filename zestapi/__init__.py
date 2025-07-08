"""
ZestAPI - A modern ASGI-compatible Python framework for building REST APIs

ZestAPI combines the best features of Flask and FastAPI while addressing their
common pain points to provide a highly productive development experience.

Key Features:
- Auto-routing via directory structure
- Built-in JWT authentication
- Rate limiting
- Plugin system
- High performance with orjson
- WebSocket support
- Comprehensive error handling
- Production-ready middleware
"""

from starlette.responses import HTMLResponse

from .core.application import ZestAPI
from .core.middleware import ErrorHandlingMiddleware, RequestLoggingMiddleware
from .core.ratelimit import RateLimitMiddleware
from .core.responses import ORJSONResponse
from .core.routing import route, websocket_route
from .core.security import JWTAuthBackend, create_access_token
from .core.settings import Settings

__version__ = "1.0.1"
__author__ = "Muhammad Adnan Sultan"
__email__ = "info.adnansultan@gmail.com"

# Alias for backward compatibility
Application = ZestAPI

__all__ = [
    "ZestAPI",
    "Application",  # Alias for backward compatibility
    "route",
    "websocket_route",
    "ORJSONResponse",
    "HTMLResponse",
    "Settings",
    "create_access_token",
    "JWTAuthBackend",
    "ErrorHandlingMiddleware",
    "RequestLoggingMiddleware",
    "RateLimitMiddleware",
]
