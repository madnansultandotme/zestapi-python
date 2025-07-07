
import importlib.util
import os
from starlette.routing import Route, WebSocketRoute

def discover_routes(routes_dir):
    discovered_routes = []
    for root, _, files in os.walk(routes_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                file_path = os.path.join(root, file)
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Determine the path prefix based on directory structure
                relative_path = os.path.relpath(root, routes_dir)
                path_prefix = "/" + relative_path.replace(os.sep, "/") if relative_path != "." else ""

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and hasattr(attr, "__route__"):
                        route_info = getattr(attr, "__route__")
                        path = path_prefix + route_info["path"]
                        methods = route_info["methods"]
                        is_websocket = route_info.get("websocket", False)

                        if is_websocket:
                            discovered_routes.append(WebSocketRoute(path, attr, name=attr_name))
                        else:
                            discovered_routes.append(Route(path, attr, methods=methods, name=attr_name))
    return discovered_routes

def route(path, methods=None):
    if methods is None:
        methods = ["GET"]
    def decorator(func):
        func.__route__ = {"path": path, "methods": methods}
        return func
    return decorator

def websocket_route(path):
    def decorator(func):
        func.__route__ = {"path": path, "websocket": True}
        return func
    return decorator


