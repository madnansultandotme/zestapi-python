from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from starlette.requests import Request
from starlette.responses import Response
from zestapi import ORJSONResponse
import logging
import time


# Base plugin class (normally imported from zestapi.core.plugin)
class BasePlugin:
    """Base class for all ZestAPI plugins"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = getattr(self, "name", self.__class__.__name__)
        self.version = getattr(self, "version", "1.0.0")
        self.is_active = False
        self.logger = logging.getLogger(f"plugin.{self.name}")

    async def initialize(self, app):
        """Initialize the plugin with the app instance"""
        self.is_active = True
        self.logger.info(f"Plugin {self.name} v{self.version} initialized")

    async def cleanup(self):
        """Cleanup plugin resources"""
        self.is_active = False
        self.logger.info(f"Plugin {self.name} cleaned up")

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status"""
        return {
            "name": self.name,
            "version": self.version,
            "active": self.is_active,
            "config": self.config,
        }


# Base middleware class (normally imported from zestapi.core.middleware)
class BaseMiddleware:
    """Base class for middleware"""

    def __init__(self):
        self.logger = logging.getLogger(f"middleware.{self.__class__.__name__}")

    async def process_request(self, request: Request) -> Optional[Response]:
        """Process incoming request. Return response to short-circuit."""
        return None

    async def process_response(self, request: Request, response: Response) -> Response:
        """Process outgoing response"""
        return response

    async def process_exception(
        self, request: Request, exception: Exception
    ) -> Optional[Response]:
        """Handle exceptions"""
        return None


class RequestLoggerMiddleware(BaseMiddleware):
    """Middleware for logging requests and responses"""

    def __init__(self, log_level: str = "INFO", include_body: bool = False):
        super().__init__()
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.include_body = include_body
        self.logger.setLevel(self.log_level)

    async def process_request(self, request: Request) -> Optional[Response]:
        """Log incoming request"""
        start_time = time.time()

        # Store start time for response timing
        request.state.start_time = start_time

        # Log request details
        self.logger.log(
            self.log_level,
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}",
        )

        # Log headers if debug level
        if self.logger.isEnabledFor(logging.DEBUG):
            headers = dict(request.headers)
            self.logger.debug(f"Request headers: {headers}")

        return None  # Continue processing

    async def process_response(self, request, response):
        """Log outgoing response"""
        end_time = time.time()
        start_time = getattr(request.state, "start_time", end_time)
        duration = (end_time - start_time) * 1000  # Convert to milliseconds

        # Log response
        self.logger.log(
            self.log_level,
            f"Response: {response.status_code} for {request.method} {request.url.path} "
            f"({duration:.2f}ms)",
        )

        # Add custom header
        response.headers["X-Request-ID"] = f"req_{int(start_time * 1000000)}"
        response.headers["X-Response-Time"] = f"{duration:.2f}ms"

        return response


class APIKeyMiddleware(BaseMiddleware):
    """Middleware for API key authentication"""

    def __init__(
        self,
        api_keys: List[str],
        header_name: str = "X-API-Key",
        protected_paths: Optional[List[str]] = None,
    ):
        super().__init__()
        self.api_keys = set(api_keys)
        self.header_name = header_name
        self.protected_paths = protected_paths or ["/protected", "/admin"]

    async def process_request(self, request: Request) -> Optional[Response]:
        """Check API key for protected paths"""
        path = request.url.path

        # Check if path requires authentication
        if not any(path.startswith(protected) for protected in self.protected_paths):
            return None  # Not protected, continue

        # Get API key from header
        api_key = request.headers.get(self.header_name)

        if not api_key:
            return ORJSONResponse(
                {"error": f"Missing {self.header_name} header"}, status_code=401
            )

        if api_key not in self.api_keys:
            return ORJSONResponse({"error": "Invalid API key"}, status_code=403)

        # Store authenticated API key in request state
        request.state.api_key = api_key
        self.logger.info(f"API key authenticated for {path}")

        return None  # Continue processing


class RequestLoggerPlugin(BasePlugin):
    """Plugin for logging HTTP requests and responses"""

    name = "request_logger"
    version = "1.0.0"
    description = "Logs HTTP requests and responses with timing information"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.log_level = self.config.get("log_level", "INFO")
        self.include_body = self.config.get("include_body", False)
        self.middleware = None

    async def initialize(self, app):
        """Initialize the request logger plugin"""
        self.middleware = RequestLoggerMiddleware(
            log_level=self.log_level, include_body=self.include_body
        )

        # Add middleware to app (simplified registration)
        if hasattr(app, "middleware_stack"):
            app.middleware_stack.append(self.middleware)

        await super().initialize(app)
        self.logger.info(f"Request logger initialized with level: {self.log_level}")


class APIKeyPlugin(BasePlugin):
    """Plugin for API key authentication"""

    name = "api_key_auth"
    version = "1.0.0"
    description = "Provides API key authentication for protected endpoints"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_keys = self.config.get("api_keys", ["test-api-key-123"])
        self.header_name = self.config.get("header_name", "X-API-Key")
        self.protected_paths = self.config.get(
            "protected_paths", ["/protected", "/admin"]
        )
        self.middleware = None

    async def initialize(self, app):
        """Initialize the API key authentication plugin"""
        self.middleware = APIKeyMiddleware(
            api_keys=self.api_keys,
            header_name=self.header_name,
            protected_paths=self.protected_paths,
        )

        # Add middleware to app (simplified registration)
        if hasattr(app, "middleware_stack"):
            app.middleware_stack.append(self.middleware)

        await super().initialize(app)
        self.logger.info(f"API key auth initialized with {len(self.api_keys)} keys")

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status"""
        status = super().get_status()
        status.update(
            {
                "api_key_count": len(self.api_keys),
                "header_name": self.header_name,
                "protected_paths": self.protected_paths,
            }
        )
        return status
