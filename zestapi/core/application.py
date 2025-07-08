import importlib.util
import logging
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import BaseRoute, Route, WebSocketRoute

from .middleware import ErrorHandlingMiddleware, RequestLoggingMiddleware
from .ratelimit import RateLimitMiddleware
from .routing import discover_routes
from .security import JWTAuthBackend
from .settings import Settings

logger = logging.getLogger(__name__)


class ZestAPI:
    """
    Main ZestAPI application class

    This class provides a high-level interface for creating ZestAPI
    applications with sensible defaults and best practices built-in.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        routes_dir: Optional[str] = None,
        plugins_dir: Optional[str] = None,
    ):
        self.settings = settings or Settings()
        self.routes_dir = routes_dir or "app/routes"
        self.plugins_dir = plugins_dir or "app/plugins"
        self._routes: List[BaseRoute] = []
        self._app: Optional[Starlette] = None
        self._error_handlers: Dict[Any, Callable] = {}

        # Configure logging
        self._setup_logging()

        # Validate settings
        self._validate_settings()

    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        try:
            log_level = getattr(logging, self.settings.log_level.upper())
            logging.basicConfig(
                level=log_level,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.StreamHandler(sys.stdout),
                    (
                        logging.FileHandler("zestapi.log")
                        if not self.settings.debug
                        else logging.NullHandler()
                    ),
                ],
            )
            logger.info(
                f"Logging configured at {self.settings.log_level.upper()} " f"level"
            )
        except Exception as e:
            logger.warning(f"Failed to setup logging: {e}")
            logging.basicConfig(level=logging.INFO)

    def _validate_settings(self) -> None:
        """Validate application settings"""
        if (
            not self.settings.jwt_secret
            or self.settings.jwt_secret == "your-secret-key"
        ):
            if not self.settings.debug:
                raise ValueError("JWT_SECRET must be set for production use")
            logger.warning("Using default JWT secret - not suitable for production")

        if self.settings.port < 1 or self.settings.port > 65535:
            raise ValueError(f"Invalid port number: {self.settings.port}")

        logger.info("Settings validation completed")

    def add_route(
        self,
        path: str,
        endpoint: Callable,
        methods: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> None:
        """Add a route to the application"""
        if methods is None:
            methods = ["GET"]

        try:
            route = Route(path, endpoint, methods=methods, name=name)
            self._routes.append(route)
            logger.debug(f"Route added: {methods} {path}")
        except Exception as e:
            logger.error(f"Failed to add route {path}: {e}")
            raise ValueError(f"Invalid route configuration: {e}")

    def add_websocket_route(
        self, path: str, endpoint: Callable, name: Optional[str] = None
    ) -> None:
        """Add a WebSocket route to the application"""
        try:
            route = WebSocketRoute(path, endpoint, name=name)
            self._routes.append(route)
            logger.debug(f"WebSocket route added: {path}")
        except Exception as e:
            logger.error(f"Failed to add WebSocket route {path}: {e}")
            raise ValueError(f"Invalid WebSocket route configuration: {e}")

    def route(
        self,
        path: str,
        methods: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Callable:
        """Decorator for adding routes to the application"""

        def decorator(func: Callable) -> Callable:
            self.add_route(path, func, methods=methods, name=name)
            return func

        return decorator

    def websocket_route(self, path: str, name: Optional[str] = None) -> Callable:
        """Decorator for adding WebSocket routes to the application"""

        def decorator(func: Callable) -> Callable:
            self.add_websocket_route(path, func, name=name)
            return func

        return decorator

    def include_router(self, router: Any) -> None:
        """Include routes from a router"""
        try:
            if hasattr(router, "routes"):
                self._routes.extend(router.routes)
                logger.info(f"Router included with {len(router.routes)} routes")
            else:
                raise ValueError("Router must have 'routes' attribute")
        except Exception as e:
            logger.error(f"Failed to include router: {e}")
            raise e

    def add_middleware(self, middleware_class: Any, **kwargs: Any) -> None:
        """Add middleware to the application"""
        if self._app:
            try:
                self._app.add_middleware(middleware_class, **kwargs)
                logger.debug(f"Middleware added: {middleware_class.__name__}")
            except Exception as e:
                logger.error(
                    f"Failed to add middleware {middleware_class.__name__}: " f"{e}"
                )
                raise e
        else:
            logger.warning("Cannot add middleware - app not created yet")

    def add_exception_handler(self, exc_class: Any, handler: Callable) -> None:
        """Add custom exception handler"""
        self._error_handlers[exc_class] = handler
        if self._app:
            self._app.add_exception_handler(exc_class, handler)
        logger.debug(f"Exception handler added for {exc_class}")

    def _discover_routes(self) -> None:
        """Discover routes from the routes directory"""
        if not self.routes_dir:
            logger.info("No routes directory specified, skipping route discovery")
            return

        routes_path = Path(self.routes_dir)
        if not routes_path.exists():
            logger.warning(f"Routes directory not found: {self.routes_dir}")
            return

        try:
            discovered_routes = discover_routes(self.routes_dir)
            self._routes.extend(discovered_routes)
            logger.info(
                f"Discovered {len(discovered_routes)} routes from " f"{self.routes_dir}"
            )
        except Exception as e:
            logger.error(f"Failed to discover routes from {self.routes_dir}: {e}")
            if not self.settings.debug:
                raise RuntimeError(f"Route discovery failed: {e}")

    def _load_plugins(self) -> None:
        """Load plugins from the plugins directory"""
        if not self.plugins_dir or not self.settings.enabled_plugins:
            logger.info("No plugins configured")
            return

        plugins_path = Path(self.plugins_dir)
        if not plugins_path.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return

        try:
            for plugin_name in self.settings.enabled_plugins:
                plugin_file = plugins_path / f"{plugin_name}.py"
                if plugin_file.exists():
                    spec = importlib.util.spec_from_file_location(
                        plugin_name, str(plugin_file)
                    )
                    if spec and spec.loader:
                        plugin_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(plugin_module)
                        logger.info(f"Plugin loaded: {plugin_name}")
                else:
                    logger.warning(f"Plugin file not found: {plugin_file}")
        except Exception as e:
            logger.error(f"Failed to load plugins: {e}")
            if not self.settings.debug:
                raise RuntimeError(f"Plugin loading failed: {e}")

    def create_app(self) -> Starlette:
        """Create and configure the Starlette application"""
        try:
            # Discover routes
            self._discover_routes()

            # Load plugins
            self._load_plugins()

            # Create Starlette app
            self._app = Starlette(
                routes=self._routes,
                debug=self.settings.debug,
            )

            # Add authentication middleware if JWT secret is configured
            if (
                self.settings.jwt_secret
                and self.settings.jwt_secret != "your-secret-key"
            ):
                self._app.add_middleware(
                    AuthenticationMiddleware,
                    backend=JWTAuthBackend(),
                )
                logger.info("JWT authentication middleware enabled")
            else:
                logger.warning(
                    "JWT authentication middleware disabled - "
                    "JWT_SECRET not configured"
                )

            # Add CORS middleware
            if self.settings.cors_origins:
                self._app.add_middleware(
                    CORSMiddleware,
                    allow_origins=self.settings.cors_origins,
                    allow_credentials=self.settings.cors_allow_credentials,
                    allow_methods=self.settings.cors_allow_methods,
                    allow_headers=self.settings.cors_allow_headers,
                )
                logger.info("CORS middleware enabled")

            # Add rate limiting middleware
            if self.settings.rate_limit:
                self._app.add_middleware(RateLimitMiddleware)
                logger.info("Rate limiting middleware enabled")

            # Add error handling middleware
            self._app.add_middleware(ErrorHandlingMiddleware)

            # Add request logging middleware
            self._app.add_middleware(RequestLoggingMiddleware)

            # Add custom exception handlers
            for exc_class, handler in self._error_handlers.items():
                self._app.add_exception_handler(exc_class, handler)

            logger.info("ZestAPI application created successfully")
            return self._app

        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            raise RuntimeError(f"Application creation failed: {e}")

    @property
    def app(self) -> Starlette:
        """Get the Starlette application instance"""
        if not self._app:
            return self.create_app()
        return self._app

    def run(self, **kwargs: Any) -> None:
        """Run the application with uvicorn"""
        try:
            import uvicorn
        except ImportError:
            raise ImportError(
                "uvicorn is required to run the application. "
                "Install with: pip install uvicorn"
            )

        uvicorn.run(
            self.app,
            host=self.settings.host,
            port=self.settings.port,
            log_level=self.settings.log_level.lower(),
            **kwargs,
        )
