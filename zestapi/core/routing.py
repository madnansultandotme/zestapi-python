import importlib.util
import os
from typing import Any, Callable, List, Optional

from starlette.routing import BaseRoute, Route, WebSocketRoute


def discover_routes(routes_dir: str) -> List[BaseRoute]:
    discovered_routes: List[BaseRoute] = []
    for root, _, files in os.walk(routes_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                file_path = os.path.join(root, file)
                try:
                    spec = importlib.util.spec_from_file_location(
                        module_name,
                        file_path,
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # Determine the path prefix based on directory
                        # structure
                        relative_path = os.path.relpath(root, routes_dir)
                        path_prefix = (
                            "/" + relative_path.replace(os.sep, "/")
                            if relative_path != "."
                            else ""
                        )

                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if callable(attr) and hasattr(attr, "__route__"):
                                route_info = getattr(attr, "__route__")
                                path = path_prefix + route_info["path"]
                                methods = route_info["methods"]
                                is_websocket = route_info.get("websocket", False)

                                if is_websocket:
                                    discovered_routes.append(
                                        WebSocketRoute(
                                            path,
                                            attr,
                                            name=attr_name,
                                        )
                                    )
                                else:
                                    discovered_routes.append(
                                        Route(
                                            path,
                                            attr,
                                            methods=methods,
                                            name=attr_name,
                                        )
                                    )
                except Exception as e:
                    # Log the error but continue processing other files
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to load route file {file_path}: {e}")
                    continue
    return discovered_routes


def route(path: str, methods: Optional[List[str]] = None) -> Callable[[Any], Any]:
    if methods is None:
        methods = ["GET"]

    def decorator(func: Any) -> Any:
        func.__route__ = {"path": path, "methods": methods}
        return func

    return decorator


def websocket_route(path: str) -> Callable[[Any], Any]:
    def decorator(func: Any) -> Any:
        func.__route__ = {"path": path, "websocket": True}
        return func

    return decorator
