
import uvicorn
import os
import orjson
import importlib.util
import logging
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from app.routing import discover_routes, route, websocket_route
from app.security import JWTAuthBackend
from app.settings import settings
from app.middleware import ErrorHandlingMiddleware, RequestLoggingMiddleware
from app.ratelimit import RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return orjson.dumps(content)


@route("/")
async def homepage(request):
    return ORJSONResponse({"hello": "world", "framework": "ZestAPI"})


@route("/health")
async def health_check(request):
    return ORJSONResponse({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2025-07-07T00:00:00Z"
    })


@websocket_route("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    await websocket.send_text("Hello, WebSocket!")
    await websocket.close()


# Discover routes from the app/routes directory
routes_dir = os.path.join(os.path.dirname(__file__), "app", "routes")
discovered_routes = discover_routes(routes_dir)

# Add the homepage, health check and websocket routes explicitly
all_routes = [
    Route("/", homepage), 
    Route("/health", health_check),
    WebSocketRoute("/ws", websocket_endpoint)
]
all_routes.extend(discovered_routes)

app = Starlette(routes=all_routes)

# Add middleware in correct order (last added = first executed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, rate_limit=settings.rate_limit)
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())


# Plugin system
plugins_dir = os.path.join(os.path.dirname(__file__), "app", "plugins")

for plugin_name in settings.enabled_plugins:
    plugin_file = os.path.join(plugins_dir, f"{plugin_name}.py")
    if os.path.exists(plugin_file):
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and hasattr(attr, "register"):
                        plugin_instance = attr(app)
                        plugin_instance.register()
                        logger.info(f"Plugin '{plugin_name}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load plugin '{plugin_name}': {e}")


if __name__ == "__main__":
    logger.info("Starting ZestAPI server...")
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        reload=settings.reload
    )


