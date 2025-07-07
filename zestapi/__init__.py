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

from .core.application import ZestAPI
from .core.routing import route, websocket_route
from .core.responses import ORJSONResponse
from .core.settings import Settings
from .core.security import create_access_token, JWTAuthBackend
from .core.middleware import ErrorHandlingMiddleware, RequestLoggingMiddleware
from .core.ratelimit import RateLimitMiddleware

__version__ = "1.0.0"
__author__ = "Muhammad Adnan Sultan"
__email__ = "info.adnansultan@gmail.com"

__all__ = [
    "ZestAPI",
    "route",
    "websocket_route",
    "ORJSONResponse",
    "Settings",
    "create_access_token",
    "JWTAuthBackend",
    "ErrorHandlingMiddleware",
    "RequestLoggingMiddleware",
    "RateLimitMiddleware",
]
